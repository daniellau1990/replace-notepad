# Fix Font Size and Highlight — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 修复字体对话框不生效 + 高亮 `==text==` 不可见

**Architecture:** 3 个文件小改：markdown_lexer.py 加方法、editor.py 调 alpha+clear 范围、app.py 加 lexer 更新调用

**Tech Stack:** Python 3.9, PyQt6, QScintilla

---

### Task 1: Fix font size not applying

**Files:**
- Modify: `notepad/src/markdown_lexer.py` (after `_set_style`)
- Modify: `notepad/src/app.py:435-439`

**Step 1: Add `update_font_size` to MarkdownLexer**

在 `markdown_lexer.py` 的 `_set_style` 方法后面（约 line 98）加入：

```python
    def update_font_size(self, size: int):
        """Reapply font size to all style definitions (0-19)."""
        for idx in range(20):
            font = self.font(idx)
            font.setPointSize(size)
            self.setFont(font, idx)
```

**Step 2: Update `_apply_font_size` in app.py**

```python
    def _apply_font_size(self, size: int):
        for _, editor, _, _ in self._tab_manager.all_editors():
            font = editor.font()
            font.setPointSize(size)
            editor.setFont(font)
            lexer = editor.lexer()
            if lexer and hasattr(lexer, 'update_font_size'):
                lexer.update_font_size(size)
```

**Step 3: Commit**

```bash
git add notepad/src/markdown_lexer.py notepad/src/app.py
git commit -m "fix: font size dialog now updates lexer styles"
```

---

### Task 2: Fix highlight visibility

**Files:**
- Modify: `notepad/src/editor.py:120-121,131`

**Step 1: Increase indicator alpha**

```python
# Line 120: 80 → 160
self.setIndicatorForegroundColor(QColor(60, 179, 113, 160), self._HL_INDIC)
```

**Step 2: Fix clearIndicatorRange end boundary**

```python
# Line 131: fix end_line and end_col
self.clearIndicatorRange(0, 0, self.lines() - 1,
                         self.lineLength(self.lines() - 1), self._HL_INDIC)
```

**Step 3: Commit**

```bash
git add notepad/src/editor.py
git commit -m "fix: increase highlight indicator alpha and fix clear range"
```

---

### Task 3: Regression test

**Step 1:** Run full pytest

```bash
cd D:\AIAGENT应用\replace_txt && python -m pytest notepad/tests/ -v
```

**Step 2:** Manual verification
- 打开 app，格式→字体→拖动滑块→确认字体实时变化
- 输入 `==test==` → 确认绿色高亮背景可见

**Step 3:** Version bump + tag

```bash
# APP_VERSION = "v0.3.9" → "v0.3.10"
git add notepad/src/app.py
git commit -m "chore: bump version to v0.3.10"
git tag v0.3.10
```
