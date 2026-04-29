import os
from PyQt6.QtWidgets import QTabWidget, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal

from src.editor import Editor


class TabManager(QTabWidget):
    """Manages open editor tabs. Ctrl+T new, Ctrl+W close."""

    rename_requested = pyqtSignal(object, str)  # Editor instance, new name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.currentChanged.connect(self._on_tab_changed)
        self.tabBar().tabBarDoubleClicked.connect(self._on_double_click)

        self._file_paths = {}       # id(editor) -> str | None
        self._dirty_editors = set()  # set of id(editor)
        self._unnamed_counter = 0
        self._default_names = {}     # id(editor) -> str

    # --- Tab creation ---

    def add_new_tab(self, content: str = "", path: str = None) -> Editor:
        editor = Editor()
        if content:
            editor.setText(content)
        editor_id = id(editor)
        self._file_paths[editor_id] = path

        if path:
            title = os.path.basename(path)
            self._default_names[editor_id] = title
        else:
            title = self._generate_unnamed_name()
            self._default_names[editor_id] = title

        self.addTab(editor, title)
        self.setCurrentWidget(editor)

        editor.textChanged.connect(lambda: self._on_editor_changed(editor))
        return editor

    def _generate_unnamed_name(self) -> str:
        self._unnamed_counter += 1
        return f"未命名文件{self._unnamed_counter}"

    # --- Editor change tracking ---

    def _on_editor_changed(self, editor):
        eid = id(editor)
        self._dirty_editors.add(eid)
        self._update_tab_title(editor)

    def _first_line(self, editor) -> str:
        text = editor.text()
        first = text.split("\n", 1)[0].strip()
        first = first.lstrip("#").strip()
        return first

    # --- Tab title ---

    def _update_tab_title(self, editor):
        eid = id(editor)
        idx = self.indexOf(editor)
        if idx < 0:
            return
        path = self._file_paths.get(eid)
        if path:
            title = os.path.basename(path)
        else:
            first = self._first_line(editor)
            title = first if first else self._default_names.get(eid, "未命名")
        if eid in self._dirty_editors:
            title += " ●"
        self.setTabText(idx, title)

    def filename_candidate(self, editor) -> str:
        """Filename suggestion from first line or default name."""
        first = self._first_line(editor)
        return first if first else self._default_names.get(id(editor), "未命名")

    # --- Dirty state ---

    def mark_dirty(self, editor_id: int):
        self._dirty_editors.add(editor_id)

    def mark_clean(self, editor_id: int):
        self._dirty_editors.discard(editor_id)

    def is_dirty(self, editor_id: int) -> bool:
        return editor_id in self._dirty_editors

    # --- Query ---

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
            self._update_tab_title(editor)

    def path_for(self, editor_id: int):  # type: -> str|None
        return self._file_paths.get(editor_id)

    def all_editors(self) -> list:
        result = []
        for i in range(self.count()):
            editor = self.widget(i)
            if editor:
                eid = id(editor)
                result.append((eid, editor, self._file_paths.get(eid), eid in self._dirty_editors))
        return result

    # --- First line title ---

    def ensure_first_line_title(self, editor):
        """If the file has a path and first line is not a heading, insert # filename."""
        eid = id(editor)
        path = self._file_paths.get(eid)
        if not path:
            return
        text = editor.text()
        first = text.split("\n", 1)[0].strip() if text else ""
        if first.startswith("# "):
            return
        basename = os.path.splitext(os.path.basename(path))[0]
        heading = f"# {basename}\n\n"
        editor.setText(heading + text)

    # --- Close / Remove ---

    def remove_tab(self, idx: int):
        widget = self.widget(idx)
        if widget:
            eid = id(widget)
            self._file_paths.pop(eid, None)
            self._dirty_editors.discard(eid)
            self._default_names.pop(eid, None)
            self.removeTab(idx)

    # --- Signals ---

    def _on_double_click(self, idx: int):
        editor = self.widget(idx)
        if not editor:
            return

        tab_bar = self.tabBar()
        tab_rect = tab_bar.tabRect(idx)

        line_edit = QLineEdit(tab_bar)
        current_text = self.tabText(idx).replace(" ●", "")
        line_edit.setText(current_text)
        line_edit.selectAll()
        line_edit.setGeometry(tab_rect.adjusted(2, 2, -2, -2))
        line_edit.show()
        line_edit.setFocus()

        def finish():
            new_text = line_edit.text().strip()
            line_edit.deleteLater()
            if new_text and new_text != current_text:
                self.rename_requested.emit(editor, new_text)

        line_edit.editingFinished.connect(finish)

    def _on_tab_changed(self, idx: int):
        if idx >= 0:
            editor = self.widget(idx)
            if editor:
                editor.setFocus()
