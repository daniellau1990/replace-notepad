## 1. Fix line spacing

- [ ] 1.1 Add `SCI_SETLINESPACING` = fontMetrics().height() in `_setup_caret()`

## 2. Fix whitespace background

- [ ] 2.1 Add `SCI_SETVIEWWS(0)` in `_setup_auto_indent()`

## 3. Verify

- [ ] 3.1 Manual: open multiline text, compare line spacing with Notepad
- [ ] 3.2 Manual: type spaces on empty line, confirm no gray background
- [ ] 3.3 Run `pytest notepad/tests/ -v` regression
