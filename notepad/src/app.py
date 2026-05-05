import os

from PyQt6.Qsci import QsciScintilla
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, \
    QStatusBar, QLabel, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QKeySequence, QFont

from src.tab_manager import TabManager
from src.autosave import AutoSave, DEFAULT_DIR
from src.file_handler import FileHandler
from src.find_replace import FindReplace
from src.settings import Settings

APP_VERSION = "v0.3.9"


class ClickablePathWidget(QWidget):
    """Status bar widget showing file path, clickable to edit."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(4, 0, 4, 0)
        self._layout.setSpacing(2)

        self._prefix = QLabel("")
        self._prefix.setStyleSheet("color: #888; font-size: 12px;")
        self._path = QLabel("(未保存)")
        self._path.setStyleSheet("color: #0066cc; font-size: 12px;")
        self._path.setCursor(Qt.CursorShape.IBeamCursor)
        self._path.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self._layout.addWidget(self._prefix)
        self._layout.addWidget(self._path)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

    def set_path(self, path: str, is_auto_save: bool = True):
        if path:
            if is_auto_save:
                self._prefix.setText("已保存 — ")
                self._prefix.setStyleSheet("color: #34c759; font-size: 12px;")
            else:
                self._prefix.setText("未保存 — ")
                self._prefix.setStyleSheet("color: #ff9500; font-size: 12px;")
            self._path.setText(path)
            self._path.setToolTip(path)
        else:
            self._prefix.setText("")
            self._path.setText("(无文件)")
            self._path.setToolTip("")

    def _on_context_menu(self, pos):
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        change_act = menu.addAction("修改默认保存路径...")
        action = menu.exec(self.mapToGlobal(pos))
        if action == change_act:
            self._change_default_dir()

    def _change_default_dir(self):
        from PyQt6.QtWidgets import QFileDialog
        from src.settings import Settings
        s = Settings()
        chosen = QFileDialog.getExistingDirectory(self, "选择默认保存路径", s.default_dir)
        if chosen:
            s.default_dir = chosen
            parent = self.window()
            if hasattr(parent, '_status'):
                parent._status.showMessage(f"默认保存路径已设为 {chosen}", 4000)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LiteNotepad")
        self.resize(900, 600)

        self._file_handler = FileHandler()
        self._settings = Settings()
        self._last_save_dir = ""
        self._prev_editor_path = ""  # previous tab's file dir for save dialog fallback

        # Center widget: tab manager fills the entire window
        self._tab_manager = TabManager()
        self.setCentralWidget(self._tab_manager)

        # Find/Replace bar
        self._find_replace = FindReplace(self)
        self._find_replace.find_next_requested.connect(self._on_find_next)
        self._find_replace.replace_requested.connect(self._on_replace)
        self._find_replace.replace_all_requested.connect(self._on_replace_all)

        # Status bar: permanent labels for line/col and path
        self._status = QStatusBar()
        self.setStatusBar(self._status)

        self._line_col_label = QLabel("第 1 行，第 1 列 | 0 行")
        self._line_col_label.setStyleSheet("font-size: 12px; padding: 0 8px;")
        self._status.addWidget(self._line_col_label)

        self._path_widget = ClickablePathWidget()
        self._status.addPermanentWidget(self._path_widget)

        self._status.addPermanentWidget(self._find_replace)
        self._find_replace.hide()

        # Auto-save
        self._autosave = AutoSave(
            get_content=lambda: self._tab_manager.current_editor().text() if self._tab_manager.current_editor() else "",
            get_path=lambda: self._tab_manager.current_path(),
            set_path=lambda p: self._tab_manager.set_current_path(p),
            status_callback=lambda msg: self._status.showMessage(msg, 3000),
            tab_manager=self._tab_manager,
            interval_ms=self._settings.auto_save_interval,
        )

        # Tab signals
        self._tab_manager.currentChanged.connect(self._on_tab_changed)
        self._tab_manager.tabBar().tabBarClicked.connect(self._on_tab_clicked)
        self._tab_manager.tabCloseRequested.connect(self._close_tab)
        self._tab_manager.rename_requested.connect(self._on_rename_requested)

        # Menu bar
        self._build_menu()

        # Apple-style clean QSS
        self.setStyleSheet("""
            QMainWindow { background: #ffffff; }
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                padding: 6px 16px;
                border: none;
                border-bottom: 2px solid transparent;
                color: #555;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                color: #000;
                border-bottom: 2px solid #007aff;
            }
            QTabBar::tab:hover:!selected {
                color: #333;
                border-bottom: 2px solid #ccc;
            }
            QStatusBar {
                background: #f5f5f5;
                border-top: 1px solid #e0e0e0;
                font-size: 12px;
            }
            QMenuBar {
                background: #fafafa;
                border-bottom: 1px solid #e0e0e0;
                font-size: 13px;
            }
            QMenuBar::item:selected {
                background: #e8e8e8;
            }
            QMenu {
                background: #ffffff;
                border: 1px solid #d0d0d0;
                padding: 4px 0;
            }
            QMenu::item {
                padding: 6px 24px;
            }
            QMenu::item:selected {
                background: #007aff;
                color: white;
            }
        """)

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
        # Record current tab's path before creating new one
        cur_path = self._tab_manager.current_path()
        if cur_path:
            self._prev_editor_path = os.path.dirname(cur_path)
        editor = self._tab_manager.add_new_tab(content, path)
        editor.textChanged.connect(self._autosave.mark_dirty)
        self._update_title()
        return editor

    def _on_tab_clicked(self, idx: int):
        """Record current tab's path before switching to another."""
        prev_path = self._tab_manager.current_path()
        if prev_path:
            self._prev_editor_path = os.path.dirname(prev_path)

    def _on_tab_changed(self, idx: int):
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

        # Shortcut menu (display-only)
        shortcut_menu = menubar.addMenu("快捷键(&K)")

        _shortcuts = [
            ("新建标签", "Ctrl+T"),
            ("打开文件", "Ctrl+O"),
            ("保存", "Ctrl+S"),
            ("另存为", "Ctrl+Shift+S"),
            ("退出", "Ctrl+Q"),
            ("加粗", "Ctrl+B"),
            ("查找/替换", "Ctrl+F"),
            ("放大", "Ctrl+滚轮上"),
            ("缩小", "Ctrl+滚轮下"),
            ("关闭标签", "Ctrl+W"),
        ]
        for label, key in _shortcuts:
            act = QAction(f"{label}    {key}", self)
            act.setEnabled(False)
            shortcut_menu.addAction(act)

        # Format menu
        format_menu = menubar.addMenu("格式(&O)")

        font_act = QAction("字体(&F)...", self)
        font_act.triggered.connect(self._show_font_dialog)
        format_menu.addAction(font_act)

        format_menu.addSeparator()

        self._wrap_action = QAction("自动换行(&W)", self)
        self._wrap_action.setCheckable(True)
        self._wrap_action.setChecked(True)
        self._wrap_action.triggered.connect(self._toggle_word_wrap)
        format_menu.addAction(self._wrap_action)

        # Version menu
        version_menu = menubar.addMenu("版本(&V)")
        version_act = QAction(APP_VERSION, self)
        version_act.setEnabled(False)
        version_menu.addAction(version_act)

    # --- File operations ---

    def _open_file(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "打开文件", "",
            "文本文件 (*.txt *.md *.markdown);;所有文件 (*)"
        )
        for path in paths:
            try:
                content = self._file_handler.read_file(path)
                editor = self._new_tab(content, path)
                self._tab_manager.ensure_first_line_title(editor)
                self._file_handler.add_recent(path)
            except Exception as e:
                QMessageBox.warning(self, "打开失败", str(e))

    def _save_file(self):
        path = self._tab_manager.current_path()
        if path:
            self._autosave.save_now()
            self._status.showMessage(f"已保存 {os.path.basename(path)}", 3000)
            return
        # Unnamed file: auto-save to default dir without dialog
        editor = self._tab_manager.current_editor()
        if not editor:
            return
        content = editor.text()
        if not content.strip():
            self._status.showMessage("内容为空，未保存", 3000)
            return
        name = self._tab_manager.filename_candidate(editor) or "未命名"
        safe_name = AutoSave._sanitize_filename(name)
        default_dir = self._settings.default_dir
        os.makedirs(default_dir, exist_ok=True)
        new_path = os.path.join(default_dir, f"{safe_name}.md")
        self._tab_manager.set_current_path(new_path)
        self._autosave.save_to_path(content, new_path)
        self._file_handler.add_recent(new_path)

    def _show_save_dialog(self):
        editor = self._tab_manager.current_editor()
        if not editor:
            return
        default_name = self._tab_manager.filename_candidate(editor)
        default_dir = self._last_save_dir
        if not default_dir:
            default_dir = self._prev_editor_path
        start_path = os.path.join(default_dir, default_name) if default_dir else default_name
        path, _ = QFileDialog.getSaveFileName(
            self, "保存", start_path,
            "Markdown (*.md);;文本文件 (*.txt);;所有文件 (*)"
        )
        if path:
            self._last_save_dir = os.path.dirname(path)
            content = editor.text()
            self._tab_manager.set_current_path(path)
            self._autosave.save_to_path(content, path)
            self._file_handler.add_recent(path)

    def _save_as_file(self):
        editor = self._tab_manager.current_editor()
        if not editor:
            return
        default_name = self._tab_manager.filename_candidate(editor)
        default_dir = self._last_save_dir
        if not default_dir:
            default_dir = self._prev_editor_path
        start_path = os.path.join(default_dir, default_name) if default_dir else default_name
        path, _ = QFileDialog.getSaveFileName(
            self, "另存为", start_path,
            "Markdown (*.md);;文本文件 (*.txt);;所有文件 (*)"
        )
        if path:
            self._last_save_dir = os.path.dirname(path)
            content = editor.text()
            self._tab_manager.set_current_path(path)
            self._autosave.save_to_path(content, path)
            self._file_handler.add_recent(path)

    def _save_with_fallback(self, content: str, target_path: str) -> tuple:
        r"""Try save to target_path. On failure, fallback to Documents\Notes\
        with auto-increment naming. Returns (actual_path, warning_msg_or_None)."""
        try:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            return target_path, None
        except OSError:
            pass

        stem = os.path.splitext(os.path.basename(target_path))[0]
        safe_stem = AutoSave._sanitize_filename(stem)
        fallback_dir = self._settings.default_dir
        os.makedirs(fallback_dir, exist_ok=True)

        counter = 1
        while True:
            suffix = f"{counter}" if counter > 1 else ""
            fallback_path = os.path.join(fallback_dir, f"{safe_stem}{suffix}.md")
            if not os.path.exists(fallback_path):
                break
            counter += 1

        try:
            with open(fallback_path, "w", encoding="utf-8") as f:
                f.write(content)
            return fallback_path, f"原路径保存失败，已保存到 {fallback_path}"
        except OSError as e:
            QMessageBox.warning(self, "保存失败", f"无法保存文件: {e}")
            return None, None

    # --- Editor actions ---

    def _toggle_bold(self):
        editor = self._tab_manager.current_editor()
        if editor:
            editor.toggle_bold()

    def _show_font_dialog(self):
        editor = self._tab_manager.current_editor()
        if not editor:
            return
        from src.font_dialog import FontSizeDialog
        dlg = FontSizeDialog(self._settings.font_size, self)
        if dlg.exec() == FontSizeDialog.DialogCode.Accepted:
            new_size = dlg.font_size
            self._settings.font_size = new_size
            self._apply_font_size(new_size)

    def _apply_font_size(self, size: int):
        for _, editor, _, _ in self._tab_manager.all_editors():
            font = editor.font()
            font.setPointSize(size)
            editor.setFont(font)

    def _toggle_word_wrap(self, checked: bool):
        from PyQt6.Qsci import QsciScintilla
        mode = QsciScintilla.WrapMode.WrapWord if checked else QsciScintilla.WrapMode.WrapNone
        for _, editor, _, _ in self._tab_manager.all_editors():
            editor.setWrapMode(mode)

    # --- Find/Replace ---

    def _on_find_next(self, text: str, case_sensitive: bool):
        editor = self._tab_manager.current_editor()
        if not editor or not text:
            return
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

    # --- Save confirmation on close ---

    def _auto_save_and_close(self, editor) -> bool:
        """Silently save dirty editor and return True (should close).
        Returns False only if both target and fallback save fail."""
        eid = id(editor)
        if not self._tab_manager.is_dirty(eid):
            return True

        content = editor.text()
        path = self._tab_manager.path_for(eid)
        if path:
            target = path
        else:
            name = self._tab_manager.filename_candidate(editor) or "未命名"
            safe_name = AutoSave._sanitize_filename(name)
            default_dir = self._settings.default_dir
            os.makedirs(default_dir, exist_ok=True)
            target = os.path.join(default_dir, f"{safe_name}.md")

        actual_path, warning = self._save_with_fallback(content, target)
        if actual_path is None:
            return False

        if actual_path != path:
            self._tab_manager.set_current_path(actual_path)
        if warning:
            self._status.showMessage(warning, 5000)
        else:
            self._status.showMessage(f"已保存 {os.path.basename(actual_path)}", 3000)
        self._tab_manager.mark_clean(eid)
        self._tab_manager._update_tab_title(editor)
        self._file_handler.add_recent(actual_path)
        return True

    def _close_tab(self, idx: int):
        editor = self._tab_manager.widget(idx)
        if not editor:
            return
        # Record closing tab's path before it's gone
        eid = id(editor)
        close_path = self._tab_manager.path_for(eid)
        if close_path:
            self._prev_editor_path = os.path.dirname(close_path)
        if self._auto_save_and_close(editor):
            self._tab_manager.remove_tab(idx)
            self._update_title()

    # --- Close window ---

    def closeEvent(self, event):
        for eid, editor, path, dirty in self._tab_manager.all_editors():
            if dirty:
                if not self._auto_save_and_close(editor):
                    event.ignore()
                    return
        self._settings.window_geometry = self.saveGeometry()
        super().closeEvent(event)

    # --- Double-click rename ---

    def _on_rename_requested(self, editor, new_text):
        from src.autosave import AutoSave
        eid = id(editor)
        clean = AutoSave._sanitize_filename(new_text)
        path = self._tab_manager.path_for(eid)

        if path:
            old_dir = os.path.dirname(path)
            ext = os.path.splitext(path)[1]
            new_path = os.path.join(old_dir, clean + ext)
            try:
                os.rename(path, new_path)
                self._tab_manager._file_paths[eid] = new_path
                self._tab_manager._update_tab_title(editor)
                self._update_title()
                self._status.showMessage(f"已重命名为 {os.path.basename(new_path)}", 3000)
            except OSError as e:
                QMessageBox.warning(self, "重命名失败", str(e))
        else:
            # Unnamed file — update default name with sanitized input
            self._tab_manager._default_names[eid] = clean
            self._tab_manager._update_tab_title(editor)

    # --- UI updates ---

    def _update_title(self):
        path = self._tab_manager.current_path()
        if path:
            self.setWindowTitle(f"{os.path.basename(path)} - LiteNotepad")
        else:
            editor = self._tab_manager.current_editor()
            if editor:
                idx = self._tab_manager.indexOf(editor)
                title = self._tab_manager.tabText(idx).replace(" ●", "")
                self.setWindowTitle(f"{title} - LiteNotepad")
            else:
                self.setWindowTitle("LiteNotepad")

    def _update_status(self):
        editor = self._tab_manager.current_editor()
        if not editor:
            return
        lines = editor.lines()
        pos = editor.getCursorPosition()
        self._line_col_label.setText(f"第 {pos[0]+1} 行，第 {pos[1]+1} 列 | {lines} 行")
        self._update_path_display()

    def _update_path_display(self):
        editor = self._tab_manager.current_editor()
        if not editor:
            self._path_widget.set_path("", is_auto_save=False)
            return
        path = self._tab_manager.current_path()
        if path:
            is_auto = not self._tab_manager.is_dirty(id(editor))
            self._path_widget.set_path(path, is_auto_save=is_auto)
        else:
            from src.autosave import DEFAULT_DIR, AutoSave
            name = self._tab_manager.filename_candidate(editor) or "未命名"
            safe = AutoSave._sanitize_filename(name)
            expected = os.path.join(DEFAULT_DIR, f"{safe}.md")
            self._path_widget.set_path(expected, is_auto_save=False)

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
