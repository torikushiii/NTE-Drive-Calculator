# 界面语言入口：加载当前语言目录并提供 tr() 显示翻译。
"""Display-language support for the English fork.

Call `install(language, root)` once at GUI startup, before the main window is
built. It loads `locales/<language>/` and patches Qt text setters so existing
Chinese source strings are shown translated without editing every call site.
`tr()` is available for text that does not pass through a patched setter.
"""

from __future__ import annotations

from pathlib import Path

from src.i18n.catalog import Catalog, load_catalog

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = {"en": "English", "zh": "简体中文"}

_catalog: Catalog | None = None
_language = "zh"


def install(language: str, root: Path) -> None:
    """Activate `language`; "zh" (the source language) leaves Qt untouched."""
    global _catalog, _language
    _language = language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
    if _language == "zh":
        _catalog = None
        return
    _catalog = load_catalog(root / "locales" / _language)
    from src.i18n.qt_patch import install_qt_patches

    install_qt_patches(tr)


def current_language() -> str:
    return _language


def tr(text: str) -> str:
    """Translate Chinese display text for the active language, else return it unchanged."""
    if _catalog is None or not isinstance(text, str):
        return text
    return _catalog.translate(text)
