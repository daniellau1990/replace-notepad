# 保存确认 + 首行标题 + 双击重命名 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add save confirmation dialogs, first-line-as-title (Obsidian-style), and double-click rename to LiteNotepad.

**Architecture:** Modify `tab_manager.py` to track per-editor dirty state and first-line titles; modify `autosave.py` to delegate dirty tracking to TabManager; modify `app.py` to show QMessageBox confirmations on close and handle rename.

**Tech Stack:** PyQt6 QMessageBox, QInputDialog, QScintilla QsciLexerMarkdown

---

## Behavior Summary

| Scenario | Behavior |
|----------|----------|
| New unnamed tab | Title = "未命名文件1/2/3..." (auto-increment) |
| User types first line | Tab title + filename auto-update to first line |
| Open named file | Insert `# filename` as line 1 (bold heading via MD lexer) |
| Auto-save (30s) | Silent save to `Documents/Notes/{first_line}.md` |
| Ctrl+S (unnamed) | Show save dialog |
| Ctrl+S (named) | Direct save (no dialog) |
| Save As | Always show save dialog |
| Close dirty tab/window | QMessageBox: **Save** / **Cancel** (no Discard) |
| Double-click tab title | QInputDialog to rename file |

---

### Task 1: `tab_manager.py` — Dirty Tracking + Title + Rename

**Files:**
- Modify: `notepad/src/tab_manager.py`
- Test: (manual, no test framework)

**Step 1: Add dirty tracking and unnamed counter**

```python
class TabManager(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        # Don't connect tabCloseRequested here — app.py handles it
        self.currentChanged.connect(self._on_tab_changed)

        self._file_paths = {}       # id(editor) -> str | None
        self._dirty_editors = set()  # set of id(editor)
        self._unnamed_counter = 0    # auto-increment for "未命名文件N"
        self._default_names = {}     # id(editor) -> str (default display name)

    def _generate_unnamed_name(self) -> str:
        self._unnamed_counter += 1
        return f"未命名文件{self._unnamed_counter}"
```

**Step 2: Add dirty tracking methods**

```python
    def mark_dirty(self, editor_id: int):
        self._dirty_editors.add(editor_id)

    def mark_clean(self, editor_id: int):
        self._dirty_editors.discard(editor_id)

    def is_dirty(self, editor_id: int) -> bool:
        return editor_id in self._dirty_editors

    def all_editors(self) -> list:
        """Return list of (editor_id, editor_widget, path, is_dirty)."""
        result = []
        for i in range(self.count()):
            editor = self.widget(i)
            if editor:
                eid = id(editor)
                result.append((eid, editor, self._file_paths.get(eid), eid in self._dirty_editors))
        return result

    def path_for(self, editor_id: int) -> str | None:
        return self._file_paths.get(editor_id)
```

**Step 3: Add first-line title tracking + update_tab_title**

```python
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

        # Connect signals
        editor.textChanged.connect(lambda: self._on_editor_changed(editor))
        return editor

    def _on_editor_changed(self, editor):
        eid = id(editor)
        self._dirty_editors.add(eid)
        self._update_tab_title(editor)

    def _first_line(self, editor) -> str:
        text = editor.text()
        first = text.split("\n", 1)[0].strip()
        # Strip markdown heading markers
        first = first.lstrip("#").strip()
        return first

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
        # Add dirty indicator
        if eid in self._dirty_editors:
            title += " ●"
        self.setTabText(idx, title)

    def filename_candidate(self, editor) -> str:
        """Get the filename candidate from first line, or default name."""
        first = self._first_line(editor)
        return first if first else self._default_names.get(id(editor), "未命名")
```

**Step 4: Add ensure_first_line_title for named files**

```python
    def ensure_first_line_title(self, editor):
        """If the file has a path and first line is not a heading, insert # filename."""
        eid = id(editor)
        path = self._file_paths.get(eid)
        if not path:
            return
        text = editor.text()
        first = text.split("\n", 1)[0].strip() if text else ""
        if first.startswith("# "):
            return  # Already has a heading
        basename = os.path.splitext(os.path.basename(path))[0]
        heading = f"# {basename}\n\n"
        editor.setText(heading + text)
```

**Step 5: Add double-click rename signal and handler**

```python
    rename_requested = pyqtSignal(object)  # Editor instance

    def __init__(self, parent=None):
        # ... existing init ...
        self.tabBar().setTabBarAutoHide(False)
        self.tabBar().tabBarDoubleClicked.connect(self._on_double_click)

    def _on_double_click(self, idx: int):
        editor = self.widget(idx)
        if editor:
            self.rename_requested.emit(editor)
```

**Step 6: Add remove_tab helper (cleanup)**

```python
    def remove_tab(self, idx: int):
        """Remove tab and clean up tracking data."""
        widget = self.widget(idx)
        if widget:
            eid = id(widget)
            self._file_paths.pop(eid, None)
            self._dirty_editors.discard(eid)
            self._default_names.pop(eid, None)
            self.removeTab(idx)
```

**Step 7: Update set_current_path**

```python
    def set_current_path(self, path: str) -> None:
        editor = self.current_editor()
        if editor:
            eid = id(editor)
            self._file_paths[eid] = path
            self._update_tab_title(editor)
```

**Step 8: Remove old `_close_tab` and `_mark_tab_changed` methods**

Delete the old `_close_tab(self, idx)` and `_mark_tab_changed(self)` methods — they're replaced by the new architecture.

**Step 9: Commit**

```bash
git add notepad/src/tab_manager.py
git commit -m "feat: add dirty tracking, first-line title, double-click rename to TabManager"
```

---

### Task 2: `autosave.py` — Delegate Dirty Tracking to TabManager

**Files:**
- Modify: `notepad/src/autosave.py`

**Step 1: Remove global dirty flag, use TabManager**

```python
import os
import re
from PyQt6.QtCore import QTimer

DEFAULT_DIR = os.path.join(os.path.expanduser("~"), "Documents", "Notes")


class AutoSave:
    def __init__(self, get_content, get_path, set_path, status_callback,
                 tab_manager, interval_ms=30000):
        self.get_content = get_content
        self.get_path = get_path
        self.set_path = set_path
        self.status_callback = status_callback
        self._tab_manager = tab_manager
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._do_save)
        self._interval_ms = interval_ms

    def mark_dirty(self):
        """Mark current editor as dirty."""
        editor = self._tab_manager.current_editor()
        if editor:
            self._tab_manager.mark_dirty(id(editor))
        self._timer.start(self._interval_ms)

    def save_now(self):
        self._timer.stop()
        content = self.get_content()
        path = self.get_path()
        if not path:
            return
        self._write(content, path)
        editor = self._tab_manager.current_editor()
        if editor:
            self._tab_manager.mark_clean(id(editor))

    def save_to_path(self, content, path):
        """Save to a specific path and mark clean."""
        self._write(content, path)
        editor = self._tab_manager.current_editor()
        if editor:
            self._tab_manager.mark_clean(id(editor))

    def _do_save(self):
        content = self.get_content()
        path = self.get_path()
        if not path:
            os.makedirs(DEFAULT_DIR, exist_ok=True)
            editor = self._tab_manager.current_editor()
            name = self._tab_manager.filename_candidate(editor) if editor else "未命名"
            safe_name = self._sanitize_filename(name)
            path = os.path.join(DEFAULT_DIR, f"{safe_name}.md")
            self.set_path(path)
        self._write(content, path)

    def _sanitize_filename(self, name: str) -> str:
        name = name[:40]
        safe = re.sub(r'[<>:"/\\|?*]', '_', name)
        return safe or "未命名"

    def _write(self, content, path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self.status_callback(f"已保存 {os.path.basename(path)}")
        except OSError as e:
            self.status_callback(f"保存失败: {e}")
```

**Step 2: Commit**

```bash
git add notepad/src/autosave.py
git commit -m "refactor: delegate dirty tracking to TabManager, add sanitize helper"
```

---

### Task 3: `app.py` — Save Confirmation Dialogs + Close Flow + Rename

**Files:**
- Modify: `notepad/src/app.py`

**Step 1: Update AutoSave init to pass tab_manager**

```python
        self._autosave = AutoSave(
            get_content=lambda: ...,
            get_path=lambda: ...,
            set_path=lambda p: self._tab_manager.set_current_path(p),
            status_callback=lambda msg: self._status.showMessage(msg, 3000),
            tab_manager=self._tab_manager,
            interval_ms=self._settings.auto_save_interval,
        )
```

**Step 2: Remove connected_editors set — TabManager handles signals now**

Remove `self._connected_editors = set()` and related logic. The signal connections are now in `tab_manager.add_new_tab()`.

**Step 3: Simplify _new_tab**

```python
    def _new_tab(self, content="", path=None):
        editor = self._tab_manager.add_new_tab(content, path)
        self._md_preview.set_editor(editor)
        self._update_title()
        # Connect textChanged for preview (only once per editor)
        eid = id(editor)
        try:
            editor.textChanged.disconnect(self._md_preview.schedule_render)
        except TypeError:
            pass
        editor.textChanged.connect(self._md_preview.schedule_render)
        return editor
```

**Step 4: Add ensure_first_line_title when opening files**

```python
    def _open_file(self):
        paths, _ = QFileDialog.getOpenFileNames(...)
        for path in paths:
            try:
                content = self._file_handler.read_file(path)
                editor = self._new_tab(content, path)
                self._tab_manager.ensure_first_line_title(editor)
                self._file_handler.add_recent(path)
            except Exception as e:
                QMessageBox.warning(self, "打开失败", str(e))
```

**Step 5: Update _save_file to show dialog for unnamed files**

```python
    def _save_file(self):
        path = self._tab_manager.current_path()
        if path:
            self._autosave.save_now()
        else:
            self._show_save_dialog()

    def _show_save_dialog(self):
        editor = self._tab_manager.current_editor()
        default_name = self._tab_manager.filename_candidate(editor) if editor else "未命名"
        path, _ = QFileDialog.getSaveFileName(
            self, "保存", default_name,
            "Markdown (*.md);;文本文件 (*.txt);;所有文件 (*)"
        )
        if path:
            content = editor.text() if editor else ""
            self._tab_manager.set_current_path(path)
            self._autosave.save_to_path(content, path)
            self._file_handler.add_recent(path)
```

**Step 6: Update _save_as_file to use save_to_path**

```python
    def _save_as_file(self):
        editor = self._tab_manager.current_editor()
        default_name = self._tab_manager.filename_candidate(editor) if editor else "未命名"
        path, _ = QFileDialog.getSaveFileName(
            self, "另存为", default_name,
            "Markdown (*.md);;文本文件 (*.txt);;所有文件 (*)"
        )
        if path:
            content = editor.text() if editor else ""
            self._tab_manager.set_current_path(path)
            self._autosave.save_to_path(content, path)
            self._file_handler.add_recent(path)
```

**Step 7: Add save confirmation dialog (Save / Cancel only)**

```python
    def _confirm_save_and_close(self, editor) -> bool:
        """Returns True if should close, False if cancelled."""
        eid = id(editor)
        if not self._tab_manager.is_dirty(eid):
            return True

        dialog = QMessageBox(self)
        dialog.setWindowTitle("LiteNotepad")
        dialog.setText("文件已修改，是否保存更改？")
        save_btn = dialog.addButton("保存", QMessageBox.ButtonRole.AcceptRole)
        cancel_btn = dialog.addButton("取消", QMessageBox.ButtonRole.RejectRole)
        dialog.setDefaultButton(save_btn)
        dialog.exec()

        if dialog.clickedButton() == cancel_btn:
            return False

        # Save button clicked
        path = self._tab_manager.path_for(eid)
        if path:
            content = editor.text()
            self._autosave.save_to_path(content, path)
        else:
            default_name = self._tab_manager.filename_candidate(editor)
            path, _ = QFileDialog.getSaveFileName(
                self, "保存", default_name,
                "Markdown (*.md);;文本文件 (*.txt);;所有文件 (*)"
            )
            if not path:
                return False  # User cancelled save dialog
            content = editor.text()
            self._tab_manager.set_current_path(path)
            self._autosave.save_to_path(content, path)
            self._file_handler.add_recent(path)
        return True
```

**Step 8: Implement close_tab handler**

```python
    # In __init__, connect tabCloseRequested:
    self._tab_manager.tabCloseRequested.connect(self._close_tab)

    def _close_tab(self, idx: int):
        editor = self._tab_manager.widget(idx)
        if not editor:
            return
        if self._confirm_save_and_close(editor):
            self._tab_manager.remove_tab(idx)
            self._update_title()
```

**Step 9: Implement closeEvent with multi-tab handling**

```python
    def closeEvent(self, event):
        # Check all tabs
        for eid, editor, path, dirty in self._tab_manager.all_editors():
            if dirty:
                if not self._confirm_save_and_close(editor):
                    event.ignore()
                    return
        self._settings.window_geometry = self.saveGeometry()
        super().closeEvent(event)
```

**Step 10: Handle double-click rename**

```python
    # In __init__:
    self._tab_manager.rename_requested.connect(self._on_rename_requested)

    def _on_rename_requested(self, editor):
        eid = id(editor)
        path = self._tab_manager.path_for(eid)
        current_name = self._tab_manager.filename_candidate(editor)

        if path:
            # Named file — rename on disk
            old_path = path
            old_dir = os.path.dirname(old_path)
            new_name, ok = QInputDialog.getText(
                self, "重命名文件", "文件名:",
                text=os.path.splitext(os.path.basename(old_path))[0]
            )
            if ok and new_name:
                new_path = os.path.join(old_dir, new_name + os.path.splitext(old_path)[1])
                try:
                    os.rename(old_path, new_path)
                    self._tab_manager._file_paths[eid] = new_path
                    self._tab_manager._update_tab_title(editor)
                    self._update_title()
                    self._status.showMessage(f"已重命名为 {os.path.basename(new_path)}", 3000)
                except OSError as e:
                    QMessageBox.warning(self, "重命名失败", str(e))
        else:
            # Unnamed file — show save dialog
            self._show_save_dialog()
```

**Step 11: Commit**

```bash
git add notepad/src/app.py
git commit -m "feat: add save confirmation dialogs, close flow, double-click rename"
```

---

### Task 4: Update `Version.md`

**Files:**
- Modify: `notepad/Version.md`

**Step 1: Add v0.2.0 entry**

```markdown
## v0.2.0 (2026-04-29)
- Feature: Save confirmation dialog on close (Save/Cancel, no Discard)
- Feature: First line auto-becomes filename (Obsidian-style, "未命名文件N" default)
- Feature: Open named files inserts `# filename` as bold heading
- Feature: Double-click tab title to rename file
- Refactor: Per-editor dirty state tracking in TabManager
```

**Step 2: Commit**

```bash
git add notepad/Version.md
git commit -m "docs: update Version.md for v0.2.0"
```

---

## Verification

1. Launch app: `cd notepad && source .venv/Scripts/activate && python main.py`
2. New tab shows "未命名文件1", type text → title updates to first line
3. Create 2nd new tab → shows "未命名文件2"
4. Wait 30s → file auto-saved to `~/Documents/Notes/{first_line}.md`
5. Ctrl+S → save dialog appears with first-line as default name
6. Close dirty tab → dialog with Save/Cancel (no Discard)
7. Open existing file → `# filename` inserted at top as bold heading
8. Double-click tab → rename dialog
9. Close window with multiple dirty tabs → confirm each, cancel one → entire close cancelled
