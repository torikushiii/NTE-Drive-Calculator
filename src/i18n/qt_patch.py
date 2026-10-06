# Qt 文本入口补丁：在显示前翻译中文原文，读取时还原原文以保持业务逻辑不变。
"""Monkeypatch PySide6 text APIs so Chinese source strings display translated.

Setters and constructors translate their string arguments. Getters used by
program logic (`text()`, `currentText()`, `itemText()`, `tabText()`, ...)
return the original Chinese source while the widget still shows the
translation of it, so comparisons such as `button.text() == "保存"` keep
working. Once the displayed text changes (user edits, C++ side updates), the
getter returns what is displayed.

Patches are applied to class attributes, so they affect every later call
regardless of import order. Install once, before widgets are created.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QAction, QPainter, QStandardItem
from PySide6.QtWidgets import (
    QAbstractButton,
    QCheckBox,
    QComboBox,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QProgressDialog,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QDoubleSpinBox,
    QFormLayout,
    QStatusBar,
    QTabBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QToolTip,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

Translate = Callable[[str], str]

# Item data role holding the untranslated source text of combo/list/table items.
SOURCE_ROLE = int(Qt.ItemDataRole.UserRole) + 0x5EED
_PROPERTY_PREFIX = "_i18n_src_"
_installed = False


def _needs_room(widget: QWidget, width: int) -> int | None:
    """Width a fixed-width button/label needs for its (longer) translated text."""
    if isinstance(widget, QLabel) and (widget.wordWrap() or not widget.text()):
        return None
    if not isinstance(widget, (QAbstractButton, QLabel)):
        return None
    # Only text we translated; icon buttons and untouched text keep their size.
    if widget.property(_PROPERTY_PREFIX + "text") is None:
        return None
    needed = widget.sizeHint().width()
    return needed if needed > width else None


def install_width_fitting() -> None:
    """Widen buttons/labels whose fixed width was chosen for shorter Chinese text.

    Only fixed or maximum widths are widened, and only when the current text
    would otherwise be clipped; heights and layouts are left alone.
    """
    set_fixed_width = QWidget.setFixedWidth
    set_maximum_width = QWidget.setMaximumWidth
    set_fixed_size = QWidget.setFixedSize

    def refit(widget: QWidget) -> None:
        """Widen a width-constrained widget if its current text no longer fits."""
        maximum = widget.maximumWidth()
        if maximum >= 16_777_215:
            return
        # A style sheet "min-width" overrides the minimum set by setFixedWidth, so
        # remember the fixed intent instead of comparing minimum and maximum.
        fixed = bool(widget.property(_FIXED_WIDTH)) or widget.minimumWidth() == maximum
        needed = _needs_room(widget, maximum)
        if not needed:
            if fixed and widget.property(_WIDENED) and widget.minimumWidth() < maximum:
                set_fixed_width(widget, maximum)
            return
        if not fixed:
            set_maximum_width(widget, needed)
            return
        set_fixed_width(widget, needed)
        widget.setProperty(_WIDENED, True)
        # Fixed-width containers sized around the old width ("name + button"
        # cards) grow by the same amount, so the widened child is not squeezed.
        grow = needed - maximum
        parent = widget.parentWidget()
        for _ in range(2):
            if parent is None or parent.isWindow() or parent.minimumWidth() != parent.maximumWidth():
                break
            set_fixed_width(parent, parent.maximumWidth() + grow)
            parent = parent.parentWidget()

    # The width is usually fixed before the widget's style sheet (bold font,
    # padding) is applied, so check again once the final style is known.
    refitter = _Refitter(refit)

    def watch(widget: QWidget, fixed: bool) -> None:
        if not isinstance(widget, (QAbstractButton, QLabel)):
            return
        if fixed:
            widget.setProperty(_FIXED_WIDTH, True)
        if not widget.property(_WATCHED):
            widget.setProperty(_WATCHED, True)
            widget.installEventFilter(refitter)

    def fixed_width(self, width):
        watch(self, True)
        return set_fixed_width(self, _needs_room(self, width) or width)

    def maximum_width(self, width):
        watch(self, False)
        return set_maximum_width(self, _needs_room(self, width) or width)

    def fixed_size(self, *args):
        watch(self, True)
        if len(args) == 2:
            width, height = args
            return set_fixed_size(self, _needs_room(self, width) or width, height)
        size = args[0]
        needed = _needs_room(self, size.width())
        return set_fixed_size(self, needed or size.width(), size.height())

    QWidget.setFixedWidth = fixed_width
    QWidget.setMaximumWidth = maximum_width
    QWidget.setFixedSize = fixed_size

    # Text set after the width was fixed: widen if the new text no longer fits.
    for cls in (QAbstractButton, QLabel):
        original = cls.setText

        def set_text(self, *args, _original=original):
            result = _original(self, *args)
            refit(self)
            return result

        cls.setText = set_text


_FIXED_WIDTH = "_i18n_fixed_width"
_WATCHED = "_i18n_refit"
_WIDENED = "_i18n_widened"
_REFIT_EVENTS = (QEvent.Type.Show, QEvent.Type.StyleChange, QEvent.Type.FontChange)


class _Refitter(QObject):
    """Event filter that re-runs width fitting when a widget's style settles."""

    def __init__(self, refit: Callable[[QWidget], None]) -> None:
        super().__init__()
        self._refit = refit

    def eventFilter(self, watched, event):  # noqa: N802 - Qt override
        if event.type() in _REFIT_EVENTS and isinstance(watched, QWidget):
            self._refit(watched)
        return False


def install_qt_patches(tr: Translate) -> None:
    global _installed
    if _installed:
        return
    _installed = True

    plain_tr = tr

    def mnemonic_tr(text: str) -> str:
        # Buttons, actions, menus and tabs treat "&" as a shortcut marker; an "&"
        # that only exists in the translation ("Discard & Lock") must be escaped.
        translated = plain_tr(text)
        if "&" in translated and "&" not in text:
            return translated.replace("&", "&&")
        return translated

    def tr_value(value: Any, translate: Translate = plain_tr) -> Any:
        if isinstance(value, str):
            return translate(value)
        if isinstance(value, (list, tuple)) and value and all(isinstance(item, str) for item in value):
            return [translate(item) for item in value]
        return value

    def tr_args(
        args: tuple[Any, ...],
        positions: tuple[int, ...] | None = None,
        translate: Translate = plain_tr,
    ) -> tuple[Any, ...]:
        return tuple(
            tr_value(arg, translate) if positions is None or index in positions else arg
            for index, arg in enumerate(args)
        )

    def first_str(args: tuple[Any, ...]) -> str | None:
        return next((arg for arg in args if isinstance(arg, str)), None)

    # -- QObject text with a remembered source ---------------------------------

    def remember(obj: QObject, key: str, source: str | None) -> None:
        if source is not None and tr(source) != source:
            obj.setProperty(_PROPERTY_PREFIX + key, source)
        elif obj.property(_PROPERTY_PREFIX + key) is not None:
            obj.setProperty(_PROPERTY_PREFIX + key, None)

    def recall(obj: QObject, key: str, displayed: str, translate: Translate = plain_tr) -> str:
        source = obj.property(_PROPERTY_PREFIX + key)
        if isinstance(source, str) and displayed == translate(source):
            return source
        return displayed

    def patch_text_pair(
        cls: type, setter: str, getter: str, key: str, translate: Translate = plain_tr
    ) -> None:
        original_set = getattr(cls, setter)
        original_get = getattr(cls, getter)

        def patched_set(self, *args):
            remember(self, key, first_str(args))
            return original_set(self, *tr_args(args, None, translate))

        def patched_get(self, *args):
            return recall(self, key, original_get(self, *args), translate)

        setattr(cls, setter, patched_set)
        setattr(cls, getter, patched_get)

    patch_text_pair(QLabel, "setText", "text", "text")
    patch_text_pair(QAbstractButton, "setText", "text", "text", mnemonic_tr)
    install_width_fitting()
    patch_text_pair(QGroupBox, "setTitle", "title", "title", mnemonic_tr)
    patch_text_pair(QWidget, "setWindowTitle", "windowTitle", "windowTitle")
    patch_text_pair(QAction, "setText", "text", "text", mnemonic_tr)

    def patch_ctor(
        cls: type,
        key: str | None = "text",
        positions: tuple[int, ...] | None = None,
        translate: Translate = plain_tr,
    ) -> None:
        original_init = cls.__init__

        def patched_init(self, *args, **kwargs):
            for name in ("text", "title"):
                if isinstance(kwargs.get(name), str):
                    kwargs[name] = translate(kwargs[name])
            translated = tr_args(args, positions, translate)
            original_init(self, *translated, **kwargs)
            if key is not None:
                source = first_str(args if positions is None else tuple(args[i] for i in positions if i < len(args)))
                if source is not None:
                    remember(self, key, source)

        cls.__init__ = patched_init

    patch_ctor(QLabel)
    for widget_cls in (QPushButton, QCheckBox, QRadioButton, QAction):
        patch_ctor(widget_cls, translate=mnemonic_tr)
    patch_ctor(QGroupBox, "title", translate=mnemonic_tr)
    patch_ctor(QMenu, "title", translate=mnemonic_tr)
    patch_ctor(QMessageBox, None)
    # QProgressDialog(labelText, cancelButtonText, minimum, maximum, parent)
    patch_ctor(QProgressDialog, None, positions=(0, 1))

    # -- Plain translating setters (nothing reads these back for logic) ----------

    def patch_setter(
        cls: type, name: str, positions: tuple[int, ...] | None = None, translate: Translate = plain_tr
    ) -> None:
        original = getattr(cls, name)

        def patched(self, *args, **kwargs):
            return original(self, *tr_args(args, positions, translate), **kwargs)

        setattr(cls, name, patched)

    for cls, name in (
        (QWidget, "setToolTip"),
        (QWidget, "setStatusTip"),
        (QWidget, "setWhatsThis"),
        (QLineEdit, "setPlaceholderText"),
        (QTextEdit, "setPlaceholderText"),
        (QPlainTextEdit, "setPlaceholderText"),
        (QComboBox, "setPlaceholderText"),
        (QMessageBox, "setText"),
        (QMessageBox, "setInformativeText"),
        (QMessageBox, "setDetailedText"),
        (QProgressBar, "setFormat"),
        (QProgressDialog, "setLabelText"),
        (QProgressDialog, "setCancelButtonText"),
        (QSpinBox, "setSuffix"),
        (QSpinBox, "setPrefix"),
        (QSpinBox, "setSpecialValueText"),
        (QDoubleSpinBox, "setSuffix"),
        (QDoubleSpinBox, "setPrefix"),
        (QDoubleSpinBox, "setSpecialValueText"),
        (QStatusBar, "showMessage"),
        (QTableWidget, "setHorizontalHeaderLabels"),
        (QTableWidget, "setVerticalHeaderLabels"),
        (QTreeWidget, "setHeaderLabels"),
        (QTreeWidget, "setHeaderLabel"),
        (QTabBar, "setTabToolTip"),
        (QTabWidget, "setTabToolTip"),
        (QPainter, "drawText"),
    ):
        patch_setter(cls, name)
    # QFormLayout builds the row label in C++ from the string argument.
    patch_setter(QFormLayout, "addRow")
    patch_setter(QFormLayout, "insertRow")
    for name in ("setTitle", "addAction", "addMenu", "addSection"):
        patch_setter(QMenu, name, translate=mnemonic_tr)
    patch_setter(QMessageBox, "addButton", translate=mnemonic_tr)
    patch_setter(QDialogButtonBox, "addButton", translate=mnemonic_tr)

    # Read-only text views show messages and reports; editable ones hold user data.
    for cls in (QTextEdit, QPlainTextEdit):
        for name in ("setPlainText", "setHtml", "setText", "appendPlainText", "append"):
            if not hasattr(cls, name):
                continue
            original = getattr(cls, name)

            def patched(self, *args, _original=original):
                if self.isReadOnly():
                    args = tr_args(args)
                return _original(self, *args)

            setattr(cls, name, patched)

    original_tooltip = QToolTip.showText

    def show_text(*args, **kwargs):
        return original_tooltip(*tr_args(args), **kwargs)

    QToolTip.showText = staticmethod(show_text)

    # -- Static dialogs -----------------------------------------------------------

    for name in ("information", "warning", "critical", "question", "about"):
        original_static = getattr(QMessageBox, name)

        def message_box(*args, _original=original_static, **kwargs):
            return _original(*tr_args(args), **kwargs)

        setattr(QMessageBox, name, staticmethod(message_box))

    original_get_text = QInputDialog.getText

    def get_text(*args, **kwargs):
        # (parent, title, label, echo, text, ...): keep the prefilled value as-is.
        return original_get_text(*tr_args(args, (1, 2)), **kwargs)

    QInputDialog.getText = staticmethod(get_text)

    for name in ("getInt", "getDouble", "getMultiLineText"):
        original_static = getattr(QInputDialog, name)

        def input_dialog(*args, _original=original_static, **kwargs):
            return _original(*tr_args(args, (1, 2)), **kwargs)

        setattr(QInputDialog, name, staticmethod(input_dialog))

    original_get_item = QInputDialog.getItem

    def get_item(*args, **kwargs):
        # (parent, title, label, items, ...): return the chosen source item.
        items = args[3] if len(args) > 3 else kwargs.get("items")
        result, accepted = original_get_item(*tr_args(args, (1, 2, 3)), **kwargs)
        if items:
            for item in items:
                if isinstance(item, str) and tr(item) == result:
                    return item, accepted
        return result, accepted

    QInputDialog.getItem = staticmethod(get_item)

    for name in ("getOpenFileName", "getOpenFileNames", "getSaveFileName", "getExistingDirectory"):
        original_static = getattr(QFileDialog, name)

        def file_dialog(*args, _original=original_static, **kwargs):
            # (parent, caption, dir, filter): never translate the directory path.
            for key in ("caption", "filter"):
                if isinstance(kwargs.get(key), str):
                    kwargs[key] = tr(kwargs[key])
            return _original(*tr_args(args, (1, 3)), **kwargs)

        setattr(QFileDialog, name, staticmethod(file_dialog))

    # -- Combo boxes: translated display, source kept in SOURCE_ROLE --------------

    def combo_source(combo: QComboBox, index: int, displayed: str) -> str:
        source = combo.itemData(index, SOURCE_ROLE)
        if isinstance(source, str) and displayed == tr(source):
            return source
        return displayed

    combo_add_item = QComboBox.addItem
    combo_insert_item = QComboBox.insertItem
    combo_set_item_text = QComboBox.setItemText
    combo_item_text = QComboBox.itemText
    combo_current_text = QComboBox.currentText
    combo_find_text = QComboBox.findText

    def add_item(self, *args, **kwargs):
        source = first_str(args)
        combo_add_item(self, *_translate_combo_args(args), **kwargs)
        if source is not None:
            self.setItemData(self.count() - 1, source, SOURCE_ROLE)

    def insert_item(self, index, *args, **kwargs):
        source = first_str(args)
        combo_insert_item(self, index, *_translate_combo_args(args), **kwargs)
        if source is not None:
            position = index if 0 <= index < self.count() else self.count() - 1
            self.setItemData(position, source, SOURCE_ROLE)

    def _translate_combo_args(args: tuple[Any, ...]) -> tuple[Any, ...]:
        # Only the label is display text; userData (any later positional) is not.
        translated = list(args)
        for position, arg in enumerate(args):
            if isinstance(arg, str):
                translated[position] = tr(arg)
                break
        return tuple(translated)

    def add_items(self, texts):
        for text in texts:
            add_item(self, text)

    def insert_items(self, index, texts):
        for offset, text in enumerate(texts):
            insert_item(self, index + offset, text)

    def set_item_text(self, index, text):
        self.setItemData(index, text, SOURCE_ROLE)
        combo_set_item_text(self, index, tr(text))

    def item_text(self, index):
        return combo_source(self, index, combo_item_text(self, index))

    def current_text(self):
        displayed = combo_current_text(self)
        index = self.currentIndex()
        if index < 0 or combo_item_text(self, index) != displayed:
            # Editable combos may show an item's translation without selecting it.
            index = combo_find_text(self, displayed, Qt.MatchExactly) if displayed else -1
            if index < 0:
                return displayed
        return combo_source(self, index, displayed)

    def item_source_display(combo: QComboBox, text: Any) -> Any:
        """Translation of `text` when it is the source of one of the combo's items."""
        if not isinstance(text, str) or not text:
            return text
        translated = tr(text)
        if translated == text:
            return text
        index = combo_find_text(combo, translated, Qt.MatchExactly)
        if index >= 0 and combo.itemData(index, SOURCE_ROLE) == text:
            return translated
        return text

    combo_set_current_text = QComboBox.setCurrentText
    combo_set_edit_text = QComboBox.setEditText

    def set_current_text(self, text):
        combo_set_current_text(self, item_source_display(self, text))

    def set_edit_text(self, text):
        combo_set_edit_text(self, item_source_display(self, text))

    # SearchableComboBox writes the chosen item's source straight into its line edit.
    line_edit_set_text = QLineEdit.setText

    def line_edit_text(self, text):
        combo = self.parentWidget()
        if isinstance(combo, QComboBox) and combo.lineEdit() is self:
            text = item_source_display(combo, text)
        line_edit_set_text(self, text)

    QComboBox.setCurrentText = set_current_text
    QComboBox.setEditText = set_edit_text
    QLineEdit.setText = line_edit_text

    def find_text(self, text, *args):
        found = combo_find_text(self, text, *args)
        if found < 0 and isinstance(text, str):
            found = combo_find_text(self, tr(text), *args)
        return found

    QComboBox.addItem = add_item
    QComboBox.insertItem = insert_item
    QComboBox.addItems = add_items
    QComboBox.insertItems = insert_items
    QComboBox.setItemText = set_item_text
    QComboBox.itemText = item_text
    QComboBox.currentText = current_text
    QComboBox.findText = find_text

    # -- Tabs: the page widget remembers its source label ----------------------

    tab_add = QTabWidget.addTab
    tab_insert = QTabWidget.insertTab
    tab_set_text = QTabWidget.setTabText
    tab_text = QTabWidget.tabText

    def add_tab(self, page, *args):
        remember(page, "tab", first_str(args))
        return tab_add(self, page, *tr_args(args, None, mnemonic_tr))

    def insert_tab(self, index, page, *args):
        remember(page, "tab", first_str(args))
        return tab_insert(self, index, page, *tr_args(args, None, mnemonic_tr))

    def set_tab_text(self, index, text):
        page = self.widget(index)
        if page is not None:
            remember(page, "tab", text)
        return tab_set_text(self, index, mnemonic_tr(text))

    def get_tab_text(self, index):
        displayed = tab_text(self, index)
        page = self.widget(index)
        return displayed if page is None else recall(page, "tab", displayed, mnemonic_tr)

    QTabWidget.addTab = add_tab
    QTabWidget.insertTab = insert_tab
    QTabWidget.setTabText = set_tab_text
    QTabWidget.tabText = get_tab_text

    bar_add = QTabBar.addTab
    bar_insert = QTabBar.insertTab
    bar_set_text = QTabBar.setTabText
    QTabBar.addTab = lambda self, *args: bar_add(self, *tr_args(args, None, mnemonic_tr))
    QTabBar.insertTab = lambda self, index, *args: bar_insert(self, index, *tr_args(args, None, mnemonic_tr))
    QTabBar.setTabText = lambda self, index, text: bar_set_text(self, index, mnemonic_tr(text))

    # -- Item classes (not QObjects): source kept in SOURCE_ROLE ----------------

    def patch_item(cls: type) -> None:
        original_init = cls.__init__
        original_set = cls.setText
        original_get = cls.text

        def patched_init(self, *args, **kwargs):
            source = next((arg for arg in args if isinstance(arg, str)), None)
            original_init(self, *tr_args(args), **kwargs)
            if source is not None and tr(source) != source:
                self.setData(SOURCE_ROLE, source)

        def patched_set(self, text):
            self.setData(SOURCE_ROLE, text if tr(text) != text else None)
            original_set(self, tr(text))

        def patched_get(self):
            displayed = original_get(self)
            source = self.data(SOURCE_ROLE)
            if isinstance(source, str) and displayed == tr(source):
                return source
            return displayed

        cls.__init__ = patched_init
        cls.setText = patched_set
        cls.text = patched_get

    for item_cls in (QTableWidgetItem, QListWidgetItem, QStandardItem):
        patch_item(item_cls)

    original_list_add = QListWidget.addItem
    original_list_add_items = QListWidget.addItems

    def list_add_item(self, item):
        if isinstance(item, str):
            item = QListWidgetItem(item)
        return original_list_add(self, item)

    def list_add_items(self, labels):
        for label in labels:
            list_add_item(self, label)

    QListWidget.addItem = list_add_item
    QListWidget.addItems = list_add_items

    tree_init = QTreeWidgetItem.__init__
    tree_set_text = QTreeWidgetItem.setText
    tree_text = QTreeWidgetItem.text

    def tree_item_init(self, *args, **kwargs):
        sources = next((arg for arg in args if isinstance(arg, list)), None)
        tree_init(self, *tr_args(args), **kwargs)
        if sources:
            for column, source in enumerate(sources):
                if isinstance(source, str) and tr(source) != source:
                    self.setData(column, SOURCE_ROLE, source)

    def tree_item_set_text(self, column, text):
        self.setData(column, SOURCE_ROLE, text if tr(text) != text else None)
        tree_set_text(self, column, tr(text))

    def tree_item_text(self, column):
        displayed = tree_text(self, column)
        source = self.data(column, SOURCE_ROLE)
        if isinstance(source, str) and displayed == tr(source):
            return source
        return displayed

    QTreeWidgetItem.__init__ = tree_item_init
    QTreeWidgetItem.setText = tree_item_set_text
    QTreeWidgetItem.text = tree_item_text
