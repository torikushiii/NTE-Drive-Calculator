# 界面翻译审计：离屏启动应用，逐页截图并列出仍显示为中文的界面文本。
"""Open every main-window page offscreen and report Chinese text still on screen.

    python tools/i18n/audit_ui.py [--out build/i18n/audit] [--wait 1500]

Writes `<out>/<page>.png` screenshots, `<out>/untranslated.json`
({text: [page/widget class, ...]}) and `<out>/clipped.json` (buttons/labels
narrower than their text), then prints a summary. Displayed text is
read through Qt properties, so it reflects what users see rather than the
Chinese source returned by the patched getters.

On non-Windows hosts, Windows-only modules (winsound, keyboard, OCR runtimes,
...) are stubbed so the UI can be rendered for review; nothing touches a game.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_CJK = re.compile(r"[㐀-鿿]")


def _stub_windows_modules() -> None:
    import ctypes
    import importlib.abc
    import importlib.machinery
    from unittest import mock

    stubbed = {
        "winsound", "winreg", "keyboard", "pyautogui", "vgamepad", "win32api", "win32con",
        "win32gui", "win32process", "pywintypes", "msvcrt", "rapidocr_onnxruntime",
        "rapidocr_openvino", "onnxruntime", "pydirectinput",
    }

    class StubFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
        def find_spec(self, name, path, target=None):
            if name.split(".")[0] in stubbed:
                return importlib.machinery.ModuleSpec(name, self, is_package=True)
            return None

        def create_module(self, spec):
            module = mock.MagicMock(name=spec.name)
            module.__path__ = []
            module.__spec__ = spec
            return module

        def exec_module(self, module):
            pass

    sys.meta_path.insert(0, StubFinder())
    if not hasattr(ctypes, "windll"):
        ctypes.windll = mock.MagicMock()
        ctypes.WinDLL = mock.MagicMock()
        ctypes.WINFUNCTYPE = ctypes.CFUNCTYPE


def _displayed_texts(root) -> list[tuple[str, str]]:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QAbstractButton, QComboBox, QGroupBox, QLabel, QTabBar, QTableWidget, QTreeWidget,
        QListWidget, QWidget,
    )

    found: list[tuple[str, str]] = []
    for widget in [root, *root.findChildren(QWidget)]:
        if not widget.isVisibleTo(root):
            continue
        kind = type(widget).__name__
        texts: list[str] = [widget.toolTip()]
        if isinstance(widget, (QLabel, QAbstractButton)):
            texts.append(widget.property("text"))
        if isinstance(widget, QGroupBox):
            texts.append(widget.property("title"))
        if isinstance(widget, QComboBox):
            texts += [widget.itemData(i, Qt.ItemDataRole.DisplayRole) for i in range(widget.count())]
            texts.append(widget.property("placeholderText"))
        if isinstance(widget, QTabBar):
            texts += [widget.tabText(i) for i in range(widget.count())]
        if isinstance(widget, QTableWidget):
            for row in range(min(widget.rowCount(), 50)):
                for column in range(widget.columnCount()):
                    item = widget.item(row, column)
                    if item is not None:
                        texts.append(item.data(Qt.ItemDataRole.DisplayRole))
            for column in range(widget.columnCount()):
                header = widget.horizontalHeaderItem(column)
                if header is not None:
                    texts.append(header.data(Qt.ItemDataRole.DisplayRole))
        if isinstance(widget, QListWidget):
            texts += [widget.item(i).data(Qt.ItemDataRole.DisplayRole) for i in range(min(widget.count(), 50))]
        if isinstance(widget, QTreeWidget):
            header = widget.headerItem()
            texts += [header.data(c, Qt.ItemDataRole.DisplayRole) for c in range(header.columnCount())]
        for text in texts:
            if isinstance(text, str) and _CJK.search(text):
                found.append((text, kind))
    return found


def _clipped_texts(root) -> list[tuple[str, str]]:
    """Visible buttons/single-line labels narrower than their text needs."""
    from PySide6.QtWidgets import QAbstractButton, QLabel

    clipped: list[tuple[str, str]] = []
    for widget in [*root.findChildren(QAbstractButton), *root.findChildren(QLabel)]:
        if not widget.isVisibleTo(root) or (isinstance(widget, QLabel) and widget.wordWrap()):
            continue
        text = widget.property("text")
        if not isinstance(text, str) or not text.strip() or text.lstrip().startswith("<"):
            continue
        needed, width = widget.sizeHint().width(), widget.width()
        if needed > width + 2:
            clipped.append((text, f"{type(widget).__name__} {width}<{needed}px"))
    return clipped


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "build" / "i18n" / "audit")
    parser.add_argument("--wait", type=int, default=1500, help="ms to let each page settle")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if sys.platform != "win32":
        _stub_windows_modules()

    import src.ui.app as app_module
    import src.ui.gui_startup as gui_startup
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QDialog

    from src.ui.navigation import NAV_ITEMS

    report: dict[str, list[str]] = {}
    clipped: dict[str, list[str]] = {}

    def close_dialogs() -> None:
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QDialog) and widget.isVisible():
                record(widget, f"dialog:{type(widget).__name__}")
                widget.reject()

    def record(widget, page: str) -> None:
        for found, collect in ((report, _displayed_texts), (clipped, _clipped_texts)):
            for text, kind in collect(widget):
                found.setdefault(text, [])
                if f"{page}/{kind}" not in found[text]:
                    found[text].append(f"{page}/{kind}")

    def run(window) -> None:
        window.resize(1600, 1000)
        steps = list(enumerate(NAV_ITEMS))

        def step() -> None:
            close_dialogs()
            if not steps:
                finish()
                return
            _, item = steps.pop(0)
            try:
                window._go(item.key)
            except Exception as exc:  # report and keep auditing other pages
                print(f"{item.key}: navigation failed: {exc}")
            QTimer.singleShot(args.wait, lambda: capture(item.key))

        def capture(key: str) -> None:
            QApplication.processEvents()
            window.grab().save(str(args.out / f"{key}.png"))
            record(window, key)
            step()

        def finish() -> None:
            ordered = dict(sorted(report.items(), key=lambda entry: entry[1][0]))
            (args.out / "untranslated.json").write_text(
                json.dumps(ordered, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
            )
            (args.out / "clipped.json").write_text(
                json.dumps(clipped, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
            )
            print(f"{len(ordered)} distinct untranslated texts, {len(clipped)} clipped; screenshots in {args.out}")
            os._exit(0)

        QTimer.singleShot(args.wait * 2, step)

    original_show = app_module.MainWindow.show

    def show(self) -> None:
        original_show(self)
        run(self)

    app_module.MainWindow.show = show
    gui_startup.run_gui(
        app_module.APP_CONTEXT, app_module.GLOBAL_THEME_SETTINGS, app_module.MainWindow, lambda: None
    )


if __name__ == "__main__":
    main()
