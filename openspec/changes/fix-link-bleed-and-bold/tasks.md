## 1. Fix link color bleed

- [ ] 1.1 Change style 18 from blue+underline to neutral black in markdown_lexer.py

## 2. Fix green background drift

- [ ] 2.1 Change regex `==(.+?)==` to `==(.{2,}?)==` in editor.py `_apply_highlights`

## 3. Fix bold not working with Chinese

- [ ] 3.1 Add `_BOLD_INDIC = 9` and PlainIndicator setup in editor.py
- [ ] 3.2 Add `_apply_bold()` scanning `**text**` with indicator
- [ ] 3.3 Wire `_apply_bold` into the 300ms timer alongside `_apply_highlights`

## 4. Verify

- [ ] 4.1 Manual: drag image, confirm no blue text leak
- [ ] 4.2 Manual: type `== ==` confirm no green highlight, type `==测试==` confirm visible
- [ ] 4.3 Manual: type `文字**加粗**内容` confirm bold rendering
- [ ] 4.4 Run `pytest notepad/tests/ -v`
