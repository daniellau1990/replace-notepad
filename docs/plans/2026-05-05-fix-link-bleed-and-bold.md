# Fix Link Bleed, Green Drift, Bold — Implementation Plan

**Goal:** 修复链接颜色泄漏、绿底漂移、中文加粗失效

---

### Task 1: Fix link color bleed (#9)

**File:** `notepad/src/markdown_lexer.py:82-83`

```python
# Before:
self._set_style(18, 11, False, False, (0, 100, 200), (255, 255, 255), underline=True)
# After:
self._set_style(18, 11, False, False, (30, 30, 30), (255, 255, 255))
```

### Task 2: Fix green drift (#17)

**File:** `notepad/src/editor.py:132`

```python
# Before:
for match in re.finditer(r'==(.+?)==', text):
# After:
for match in re.finditer(r'==(.{2,}?)==', text):
```

### Task 3: Fix bold with Chinese (#18)

**File:** `notepad/src/editor.py:112-126`

Add bold indicator setup alongside highlight:

```python
def _setup_highlight(self):
    # ... existing HL_INDIC setup ...
    
    self._BOLD_INDIC = 9
    self.indicatorDefine(QsciScintilla.IndicatorStyle.PlainIndicator, self._BOLD_INDIC)
    self.setIndicatorForegroundColor(QColor(30, 30, 30), self._BOLD_INDIC)
    
    self._highlight_timer = QTimer(self)
    self._highlight_timer.setSingleShot(True)
    self._highlight_timer.timeout.connect(self._apply_styles)
    self.textChanged.connect(lambda: self._highlight_timer.start(300))

def _apply_styles(self):
    self._apply_highlights()
    self._apply_bold()

def _apply_bold(self):
    import re
    text = self.text()
    self.clearIndicatorRange(0, 0, self.lines() - 1,
                             self.lineLength(self.lines() - 1), self._BOLD_INDIC)
    for match in re.finditer(r'\*\*(.+?)\*\*', text):
        start = match.start() + 2
        end = match.end() - 2
        start_line, start_col = self.lineIndexFromPosition(start)
        end_line, end_col = self.lineIndexFromPosition(end)
        self.fillIndicatorRange(start_line, start_col, end_line, end_col, self._BOLD_INDIC)
```

### Task 4: Regression + version

v0.3.11 → v0.3.12
