## 1. Fix font size

- [ ] 1.1 Add `update_font_size(size)` method to MarkdownLexer — iterate styles 0-19, update font pointSize
- [ ] 1.2 Update `_apply_font_size()` in app.py — add `lexer.update_font_size(size)` call

## 2. Fix highlight visibility

- [ ] 2.1 Increase indicator alpha from 80 to 160 in editor.py `_setup_highlight()`
- [ ] 2.2 Fix `clearIndicatorRange` end range in `_apply_highlights()` — use `self.lines()-1` and `self.lineLength(self.lines()-1)`

## 3. Verify

- [ ] 3.1 Manual test: font size dialog changes editor text size
- [ ] 3.2 Manual test: `==highlight==` shows visible green background
- [ ] 3.3 Run `pytest notepad/tests/ -v` for regression
