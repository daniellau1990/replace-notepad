from PyQt6.QtWidgets import QTabWidget
from PyQt6.QtCore import Qt

from src.editor import Editor


class TabManager(QTabWidget):
    """Manages open editor tabs. Ctrl+T new, Ctrl+W close."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.tabCloseRequested.connect(self._close_tab)
        self.currentChanged.connect(self._on_tab_changed)

        self._file_paths = {}  # editor_id -> path or None

    def add_new_tab(self, content: str = "", path: str = None) -> Editor:
        editor = Editor()
        if content:
            editor.setText(content)
        editor_id = id(editor)
        self._file_paths[editor_id] = path

        title = self._tab_title(path)
        self.addTab(editor, title)
        self.setCurrentWidget(editor)
        editor.textChanged.connect(self._mark_tab_changed)
        return editor

    def current_editor(self) -> Editor:
        return self.currentWidget()

    def current_path(self) -> str:
        editor = self.current_editor()
        if editor:
            return self._file_paths.get(id(editor))
        return None

    def set_current_path(self, path: str) -> None:
        editor = self.current_editor()
        if editor:
            self._file_paths[id(editor)] = path
            self.setTabText(self.currentIndex(), self._tab_title(path))

    def _tab_title(self, path: str) -> str:
        if path:
            import os
            return os.path.basename(path)
        return "未命名"

    def _mark_tab_changed(self):
        editor = self.sender()
        if editor and editor == self.current_editor():
            idx = self.currentIndex()
            title = self.tabText(idx)
            if not title.endswith(" ●"):
                self.setTabText(idx, title + " ●")

    def _close_tab(self, idx: int):
        widget = self.widget(idx)
        if widget:
            editor_id = id(widget)
            self._file_paths.pop(editor_id, None)
            self.removeTab(idx)

    def _on_tab_changed(self, idx: int):
        if idx >= 0:
            editor = self.widget(idx)
            if editor:
                editor.setFocus()

    def close_all(self):
        while self.count():
            self._close_tab(0)
