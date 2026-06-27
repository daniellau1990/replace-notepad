import os
from PyQt6.QtWidgets import QTabWidget, QLineEdit, QTabBar, QStyle, QStyleOptionTab
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint
from PyQt6.QtGui import QPainter, QColor

from src.editor import Editor
from src.logger import log


class _ScrollTabBar(QTabBar):
    """QTabBar with left-side scroll buttons matching native right-side look."""

    BTN_W = 20

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUsesScrollButtons(True)
        self.setMouseTracking(True)
        self._left_hover = False
        self._right_hover = False
        self._left_press = False
        self._right_press = False

    # --- overflow detection ---

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

    def _btn_rect(self, left_btn: bool) -> QRect:
        x = 0 if left_btn else self.BTN_W
        return QRect(x, 0, self.BTN_W, self.height())

    # --- visible-tab detection ---

    def _first_visible_tab(self) -> int:
        w = self.width()
        for i in range(self.count()):
            r = self.tabRect(i)
            if r.isValid() and r.right() > 0 and r.left() < w:
                return i
        return 0

    def _last_visible_tab(self) -> int:
        w = self.width()
        for i in range(self.count() - 1, -1, -1):
            r = self.tabRect(i)
            if r.isValid() and r.left() < w and r.right() > 0:
                return i
        return max(0, self.count() - 1)

    # --- scroll ---

    def _scroll(self, delta: int):
        n = self.count()
        if n == 0:
            return
        if delta < 0:
            # Scroll left: expose a tab hidden on the left
            first = self._first_visible_tab()
            target = max(0, first - 1)
        else:
            # Scroll right: expose a tab hidden on the right
            last = self._last_visible_tab()
            target = min(n - 1, last + 1)
        try:
            self.ensureVisible(target)
        except Exception:
            log("ERROR", f"ensureVisible({target}) failed count={n} delta={delta}")

    # --- paint ---

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._tabs_overflow():
            return

        painter = QPainter(self)
        style = self.style()
        h = self.height()

        # Separator between left buttons and tabs
        painter.setPen(QColor("#d0d0d0"))
        painter.drawLine(self.BTN_W * 2, 0, self.BTN_W * 2, h)

        # Draw left-scroll button (◀)
        self._draw_btn(painter, style, left_btn=True, h=h)
        # Draw right-scroll button (▶)
        self._draw_btn(painter, style, left_btn=False, h=h)

        painter.end()

    def _draw_btn(self, painter, style, left_btn: bool, h: int):
        opt = QStyleOptionTab()
        opt.initFrom(self)
        opt.rect = self._btn_rect(left_btn)

        is_press = self._left_press if left_btn else self._right_press
        is_hover = self._left_hover if left_btn else self._right_hover

        state = QStyle.State.State_Enabled
        if is_press:
            state |= QStyle.State.State_Sunken
        elif is_hover:
            state |= QStyle.State.State_MouseOver
        if self.isActiveWindow():
            state |= QStyle.State.State_Active
        opt.state = state

        # Button panel (matching native scroller button look)
        pe_panel = QStyle.PrimitiveElement.PE_PanelButtonTool
        # Arrow indicator
        pe_arrow = (QStyle.PrimitiveElement.PE_IndicatorArrowLeft if left_btn
                    else QStyle.PrimitiveElement.PE_IndicatorArrowRight)

        # Smaller rect for the arrow (center it)
        arrow_rect = QRect(opt.rect)
        margin = 4
        arrow_rect.adjust(margin, margin * 2, -margin, -margin * 2)

        style.drawPrimitive(pe_panel, opt, painter)
        opt.rect = arrow_rect
        style.drawPrimitive(pe_arrow, opt, painter)

    # --- mouse tracking ---

    def _btn_at(self, x: int) -> int:
        """Return -1=none, 0=left_btn, 1=right_btn."""
        if not self._tabs_overflow():
            return -1
        if x < self.BTN_W:
            return 0
        if x < self.BTN_W * 2:
            return 1
        return -1

    def mousePressEvent(self, event):
        btn = self._btn_at(event.pos().x())
        if btn == 0:
            self._left_press = True
            self.update()
            return
        elif btn == 1:
            self._right_press = True
            self.update()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self._left_press:
            self._left_press = False
            self.update()
            if self._btn_at(event.pos().x()) == 0:
                self._scroll(-1)
            return
        if self._right_press:
            self._right_press = False
            self.update()
            if self._btn_at(event.pos().x()) == 1:
                self._scroll(1)
            return
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        x = event.pos().x()
        old_left = self._left_hover
        old_right = self._right_hover
        self._left_hover = (self._btn_at(x) == 0)
        self._right_hover = (self._btn_at(x) == 1)
        if self._left_hover != old_left or self._right_hover != old_right:
            self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self._left_hover = False
        self._right_hover = False
        self._left_press = False
        self._right_press = False
        self.update()
        super().leaveEvent(event)


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
