import os
from PyQt6.QtWidgets import QTabWidget, QLineEdit, QTabBar, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint, QPointF, QEvent
from PyQt6.QtGui import QPainter, QColor, QPolygon, QMouseEvent

from src.editor import Editor


class _ScrollTabBar(QTabBar):
    """QTabBar with visible left-side scroll buttons.

    Native QTabBar ALREADY has scroll buttons at both edges, but the
    left button is only ~2px wide and invisible in Fusion style.
    We paint visible buttons on the left and relay clicks to the
    native scroll mechanism via synthetic events.
    """

    BTN_W = 18

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUsesScrollButtons(True)

    def _tabs_overflow(self) -> bool:
        n = self.count()
        w = self.width()
        if n == 0 or w <= 0:
            return False
        total = 0
        for i in range(n):
            r = self.tabRect(i)
            if r.isValid() and r.width() > 0:
                total += r.width()
        return total > w

    def _btn_rect(self) -> QRect:
        return QRect(0, 0, self.BTN_W * 2, self.height())

    # --- scroll via synthetic events on native button positions ---

    def _send_native_click(self, x: int):
        """Send a mouse press+release at bar-local x to trigger native scroll."""
        y = self.height() // 2
        pos = QPointF(x, y)
        press = QMouseEvent(QEvent.Type.MouseButtonPress, pos, pos,
                            Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
                            Qt.KeyboardModifier.NoModifier)
        release = QMouseEvent(QEvent.Type.MouseButtonRelease, pos, pos,
                              Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
                              Qt.KeyboardModifier.NoModifier)
        QApplication.sendEvent(self, press)
        QApplication.sendEvent(self, release)

    def _scroll_left(self):
        """Scroll tabs RIGHT to show earlier (hidden-left) tabs."""
        # Native left-scroll button is at x=0
        self._send_native_click(0)

    def _scroll_right(self):
        """Scroll tabs LEFT to show later (hidden-right) tabs."""
        # Native right-scroll button is at right edge (~bw-46)
        self._send_native_click(self.width() - 46)

    # --- paint ---

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._tabs_overflow():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self._btn_rect()

        painter.fillRect(r, QColor("#f0f0f0"))
        painter.setPen(QColor("#d0d0d0"))
        painter.drawLine(r.topRight().x(), 0, r.topRight().x(), r.height())

        painter.setPen(QColor("#555"))
        cy = r.height() // 2

        # Left arrow (◀)
        painter.drawPolygon(QPolygon([
            QPoint(12, cy - 5), QPoint(12, cy + 5), QPoint(6, cy),
        ]))
        # Right arrow (▶)
        painter.drawPolygon(QPolygon([
            QPoint(24, cy - 5), QPoint(24, cy + 5), QPoint(30, cy),
        ]))

        painter.end()

    # --- click handling ---

    def _in_left_buttons(self, x: float) -> int:
        """Return -1=none, 0=left_btn, 1=right_btn."""
        if not self._tabs_overflow():
            return -1
        if x < self.BTN_W:
            return 0
        if x < self.BTN_W * 2:
            return 1
        return -1

    def mousePressEvent(self, event):
        btn = self._in_left_buttons(event.pos().x())
        if btn == 0:
            self._scroll_left()
            return
        elif btn == 1:
            self._scroll_right()
            return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        # Consume double-clicks on our buttons to prevent rename box
        if self._in_left_buttons(event.pos().x()) >= 0:
            return
        super().mouseDoubleClickEvent(event)


class TabManager(QTabWidget):
    """Manages open editor tabs. Ctrl+T new, Ctrl+W close."""

    rename_requested = pyqtSignal(object, str)  # Editor instance, new name

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tab_bar = _ScrollTabBar(self)
        self.setTabBar(self._tab_bar)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        self.currentChanged.connect(self._on_tab_changed)
        self._tab_bar.tabBarDoubleClicked.connect(self._on_double_click)

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
            editor.setText(f"{title}\n\n")

        tab_title = os.path.basename(path) if path else f"{title}.md"
        self.addTab(editor, tab_title)
        self.setCurrentWidget(editor)

        editor.textChanged.connect(lambda: self._on_editor_changed(editor))
        return editor

    def _generate_unnamed_name(self) -> str:
        self._unnamed_counter += 1
        return f"未命名{self._unnamed_counter}"

    # --- Editor change tracking ---

    def _on_editor_changed(self, editor):
        eid = id(editor)
        self._dirty_editors.add(eid)
        self._update_tab_title(editor)

    def _first_line(self, editor) -> str:
        text = editor.text()
        first = text.split("\n", 1)[0].strip()
        first = first.lstrip("#").strip()
        first = first.strip("*_~`|[]()")
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
            stem = os.path.splitext(self._default_names.get(eid, '未命名'))[0]
            title = f"{stem}.md"
        if eid in self._dirty_editors:
            title += " ●"
        self.setTabText(idx, title)

    def filename_candidate(self, editor) -> str:
        """Return filename stem — default name for unnamed, basename without ext for saved."""
        eid = id(editor)
        path = self._file_paths.get(eid)
        if path:
            return os.path.splitext(os.path.basename(path))[0]
        return self._default_names.get(eid, "未命名")

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
        # Always show filename stem without extension for editing
        current_text = os.path.splitext(current_text)[0]
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
