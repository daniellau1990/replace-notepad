# Silent Close Tab Save Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 关闭标签时静默自动保存到状态栏路径，不弹确认对话框，保存失败时 fallback 到 Documents\Notes\ 并自动递增编号。

**Architecture:** 仅修改 `app.py`，将 `_confirm_save_and_close()` 替换为 `_auto_save_and_close()`，新增 `_save_with_fallback()` 处理保存失败的 fallback 逻辑。

**Tech Stack:** Python 3.9, PyQt6

---

### Task 1: Add `_save_with_fallback()` helper method

**Files:**
- Modify: `notepad/src/app.py` (add method before `_auto_save_and_close`)

**Step 1: Add the method**

在 `_show_save_dialog` 方法后面（约 line 381）插入：

```python
    def _save_with_fallback(self, content: str, target_path: str) -> tuple:
        """Try save to target_path. On failure, fallback to Documents\Notes\ 
        with auto-increment naming. Returns (actual_path, warning_msg_or_None)."""
        try:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            return target_path, None
        except OSError:
            pass

        # Fallback to Documents\Notes\
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
```

**Step 2: Verify syntax**

```bash
cd D:\AIAGENT应用\replace_txt\notepad && .venv\Scripts\python -c "import py_compile; py_compile.compile('src/app.py', doraise=True)"
```

**Step 3: Commit**

```bash
git add notepad/src/app.py
git commit -m "feat: add _save_with_fallback helper for silent close tab save"
```

---

### Task 2: Replace `_confirm_save_and_close()` with `_auto_save_and_close()`

**Files:**
- Modify: `notepad/src/app.py:446-482` (replace entire method)

**Step 1: Replace the method**

删除 `_confirm_save_and_close` (lines 446-482)，在 `_save_with_fallback` 后面插入：

```python
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
            # Unnamed file — save to default dir
            name = self._tab_manager.filename_candidate(editor) or "未命名"
            safe_name = AutoSave._sanitize_filename(name)
            default_dir = self._settings.default_dir
            os.makedirs(default_dir, exist_ok=True)
            target = os.path.join(default_dir, f"{safe_name}.md")

        actual_path, warning = self._save_with_fallback(content, target)
        if actual_path is None:
            return False  # Both saves failed

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
```

**Step 2: Verify syntax**

```bash
cd D:\AIAGENT应用\replace_txt\notepad && .venv\Scripts\python -c "import py_compile; py_compile.compile('src/app.py', doraise=True)"
```

**Step 3: Commit**

```bash
git add notepad/src/app.py
git commit -m "feat: replace _confirm_save_and_close with _auto_save_and_close"
```

---

### Task 3: Update callers — `_close_tab()` and `closeEvent()`

**Files:**
- Modify: `notepad/src/app.py:484-506`

**Step 1: Update `_close_tab()`**

```python
    def _close_tab(self, idx: int):
        editor = self._tab_manager.widget(idx)
        if not editor:
            return
        eid = id(editor)
        close_path = self._tab_manager.path_for(eid)
        if close_path:
            self._prev_editor_path = os.path.dirname(close_path)
        if self._auto_save_and_close(editor):
            self._tab_manager.remove_tab(idx)
            self._update_title()
```

**Step 2: Update `closeEvent()`**

```python
    def closeEvent(self, event):
        for eid, editor, path, dirty in self._tab_manager.all_editors():
            if dirty:
                if not self._auto_save_and_close(editor):
                    event.ignore()
                    return
        self._settings.window_geometry = self.saveGeometry()
        super().closeEvent(event)
```

**Step 3: Verify syntax and run regression**

```bash
cd D:\AIAGENT应用\replace_txt\notepad && .venv\Scripts\python -c "import py_compile; py_compile.compile('src/app.py', doraise=True)"
cd D:\AIAGENT应用\replace_txt && python -m pytest tests/ -v
```

**Step 4: Commit**

```bash
git add notepad/src/app.py
git commit -m "feat: wire _auto_save_and_close into _close_tab and closeEvent"
```

---

### Task 4: Manual verification checklist

- [ ] 打开有路径文件 → 编辑 → Ctrl+W → 确认静默保存、无弹框、标签关闭
- [ ] 新建标签(Ctrl+T) → 输入内容 → Ctrl+W → 确认自动保存到 Documents\Notes\未命名N.md
- [ ] 打开干净文件（未编辑）→ Ctrl+W → 确认直接关闭、无保存
- [ ] 多标签窗口 → 编辑多个 → 关闭窗口 → 确认全部静默保存
- [ ] 模拟保存失败：在状态栏路径保存一个只读文件 → 编辑 → Ctrl+W → 确认 fallback 到 Documents\Notes\
- [ ] `pytest tests/` 全量回归通过

---

### Task 5: Version bump

**Step 1: Update version**

`APP_VERSION = "v0.3.8"` → `"v0.3.9"` in `notepad/src/app.py:15`

**Step 2: Commit and tag**

```bash
git add notepad/src/app.py
git commit -m "chore: bump version to v0.3.9"
git tag v0.3.9
```
