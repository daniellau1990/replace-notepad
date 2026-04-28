import os

from PyQt6.Qsci import QsciScintilla
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QStatusBar, QSplitter
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QKeySequence

from src.tab_manager import TabManager
from src.autosave import AutoSave
from src.file_handler import FileHandler
from src.md_preview import MarkdownPreview
from src.find_replace import FindReplace
from src.settings import Settings


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LiteNotepad")
        self.resize(900, 600)

        self._file_handler = FileHandler()
        self._settings = Settings()

        # Center widget: QSplitter with tab manager (left) + MD preview (right)
        self._tab_manager = TabManager()
        self._md_preview = MarkdownPreview()

        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.addWidget(self._tab_manager)
        self._splitter.addWidget(self._md_preview)
        self._splitter.setSizes([500, 400])
        self.setCentralWidget(self._splitter)

        # Find/Replace bar
        self._find_replace = FindReplace(self)
        self._find_replace.find_next_requested.connect(self._on_find_next)
        self._find_replace.replace_requested.connect(self._on_replace)
        self._find_replace.replace_all_requested.connect(self._on_replace_all)

        # Status bar
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.addPermanentWidget(self._find_replace)
        self._find_replace.hide()

        # Auto-save
        self._autosave = AutoSave(
            get_content=lambda: self._tab_manager.current_editor().text() if self._tab_manager.current_editor() else "",
            get_path=lambda: self._tab_manager.current_path(),
            set_path=lambda p: self._tab_manager.set_current_path(p),
            status_callback=lambda msg: self._status.showMessage(msg, 3000),
            interval_ms=self._settings.auto_save_interval,
        )

        # Track which editors already have textChanged connected
        self._connected_editors = set()

        # Tab change -> update preview + title
        self._tab_manager.currentChanged.connect(self._on_tab_changed)

        # Menu bar
        self._build_menu()

        # Default tab
        self._new_tab()

        # Restore geometry
        geo = self._settings.window_geometry
        if geo:
            self.restoreGeometry(geo)

        # Status timer
        self._cursor_timer = QTimer()
        self._cursor_timer.timeout.connect(self._update_status)
        self._cursor_timer.start(500)

    # --- Tab management ---

    def _new_tab(self, content="", path=None):
        """Create a new editor tab and connect its signals once."""
        editor = self._tab_manager.add_new_tab(content, path)
        eid = id(editor)
        if eid not in self._connected_editors:
            editor.textChanged.connect(self._autosave.mark_dirty)
            editor.textChanged.connect(self._md_preview.schedule_render)
            self._connected_editors.add(eid)
        self._md_preview.set_editor(editor)
        self._update_title()
        return editor

    def _on_tab_changed(self, idx: int):
        editor = self._tab_manager.current_editor()
        self._md_preview.set_editor(editor)
        if editor:
            self._update_title()

    # --- Menu ---

    def _build_menu(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("文件(&F)")

        new_act = QAction("新建(&N)", self)
        new_act.setShortcut(QKeySequence("Ctrl+T"))
        new_act.triggered.connect(lambda: self._new_tab())
        file_menu.addAction(new_act)

        open_act = QAction("打开(&O)...", self)
        open_act.setShortcut(QKeySequence("Ctrl+O"))
        open_act.triggered.connect(self._open_file)
        file_menu.addAction(open_act)

        save_act = QAction("保存(&S)", self)
        save_act.setShortcut(QKeySequence("Ctrl+S"))
        save_act.triggered.connect(self._save_file)
        file_menu.addAction(save_act)

        save_as_act = QAction("另存为(&A)...", self)
        save_as_act.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_act.triggered.connect(self._save_as_file)
        file_menu.addAction(save_as_act)

        file_menu.addSeparator()

        recent_menu = file_menu.addMenu("最近打开")
        self._update_recent_menu(recent_menu)

        file_menu.addSeparator()

        exit_act = QAction("退出(&X)", self)
        exit_act.setShortcut(QKeySequence("Ctrl+Q"))
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        # Edit menu
        edit_menu = menubar.addMenu("编辑(&E)")

        bold_act = QAction("加粗(&B)", self)
        bold_act.setShortcut(QKeySequence("Ctrl+B"))
        bold_act.triggered.connect(self._toggle_bold)
        edit_menu.addAction(bold_act)

        edit_menu.addSeparator()

        find_act = QAction("查找/替换(&F)", self)
        find_act.setShortcut(QKeySequence("Ctrl+F"))
        find_act.triggered.connect(self._find_replace.toggle)
        edit_menu.addAction(find_act)

        # View menu
        view_menu = menubar.addMenu("视图(&V)")

        preview_act = QAction("Markdown 预览(&P)", self)
        preview_act.setShortcut(QKeySequence("Ctrl+P"))
        preview_act.triggered.connect(self._toggle_preview)
        view_menu.addAction(preview_act)

    # --- File operations ---

    def _open_file(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "打开文件", "",
            "文本文件 (*.txt *.md *.markdown);;所有文件 (*)"
        )
        for path in paths:
            try:
                content = self._file_handler.read_file(path)
                self._new_tab(content, path)
                self._file_handler.add_recent(path)
            except Exception as e:
                QMessageBox.warning(self, "打开失败", str(e))

    def _save_file(self):
        path = self._tab_manager.current_path()
        if path:
            self._autosave.save_now()
        else:
            self._save_as_file()

    def _save_as_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "另存为", "",
            "Markdown (*.md);;文本文件 (*.txt);;所有文件 (*)"
        )
        if path:
            self._tab_manager.set_current_path(path)
            self._autosave.save_now()
            self._file_handler.add_recent(path)

    # --- Editor actions ---

    def _toggle_bold(self):
        editor = self._tab_manager.current_editor()
        if editor:
            editor.toggle_bold()

    def _toggle_preview(self):
        visible = not self._md_preview.isVisible()
        self._md_preview.setVisible(visible)
        self._status.showMessage(
            "预览已显示" if visible else "预览已隐藏", 2000
        )

    # --- Find/Replace ---

    def _on_find_next(self, text: str, case_sensitive: bool):
        editor = self._tab_manager.current_editor()
        if not editor or not text:
            return
        flags = 0
        flags = QsciScintilla.SCFIND_MATCHCASE if case_sensitive else 0
        editor.findFirst(text, False, False, False, True, flags)

    def _on_replace(self, find: str, replace: str, case_sensitive: bool):
        editor = self._tab_manager.current_editor()
        if not editor or not find:
            return
        if editor.hasSelectedText():
            editor.replaceSelectedText(replace)
        self._on_find_next(find, case_sensitive)

    def _on_replace_all(self, find: str, replace: str, case_sensitive: bool):
        editor = self._tab_manager.current_editor()
        if not editor:
            return
        editor.setCursorPosition(0, 0)
        count = 0
        while editor.findFirst(find, False, False, False, True):
            editor.replaceSelectedText(replace)
            count += 1
        self._status.showMessage(f"已替换 {count} 处", 3000)

    def _update_title(self):
        path = self._tab_manager.current_path()
        if path:
            self.setWindowTitle(f"{os.path.basename(path)} - LiteNotepad")
        else:
            self.setWindowTitle("LiteNotepad")

    def _update_status(self):
        editor = self._tab_manager.current_editor()
        if not editor:
            return
        lines = editor.lines()
        pos = editor.getCursorPosition()
        self._status.showMessage(f"第 {pos[0]+1} 行，第 {pos[1]+1} 列 | {lines} 行")

    def _update_recent_menu(self, menu):
        menu.clear()
        for path in self._file_handler.recent_files():
            act = QAction(path, self)
            act.triggered.connect(lambda checked, p=path: self._open_recent(p))
            menu.addAction(act)
        if not menu.actions():
            menu.addAction("(无)")

    def _open_recent(self, path: str):
        try:
            content = self._file_handler.read_file(path)
            self._new_tab(content, path)
        except Exception as e:
            QMessageBox.warning(self, "打开失败", str(e))

    # --- Close ---

    def closeEvent(self, event):
        self._autosave.save_now()
        self._settings.window_geometry = self.saveGeometry()
        super().closeEvent(event)
