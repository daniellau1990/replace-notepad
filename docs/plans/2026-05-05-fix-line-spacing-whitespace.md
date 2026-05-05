# Fix Line Spacing & Whitespace — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans

**Goal:** 行间距压缩匹配记事本 + 空格不再显示灰色背景

**Tech Stack:** Python 3.9, PyQt6, QScintilla

---

### Task 1: Fix line spacing

**Files:** Modify `notepad/src/editor.py:28-32`

```python
def _setup_caret(self):
    self.setCaretWidth(2)
    self.setCaretForegroundColor(QColor(0, 0, 0))
    self.setExtraAscent(0)
    self.setExtraDescent(0)
    font_metrics = self.fontMetrics()
    self.SendScintilla(QsciScintilla.SCI_SETLINESPACING, font_metrics.height())
```

### Task 2: Fix whitespace background

**Files:** Modify `notepad/src/editor.py:34-37`

```python
def _setup_auto_indent(self):
    self.setAutoIndent(True)
    self.setTabWidth(4)
    self.setIndentationGuides(False)
    self.SendScintilla(QsciScintilla.SCI_SETVIEWWS, 0)  # SCWS_INVISIBLE
```

### Task 3: Regression test + version bump

```bash
python -m pytest notepad/tests/ -v
# version v0.3.10 → v0.3.11
```
