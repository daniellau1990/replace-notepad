## Context

QsciLexerMarkdown C++ lexer 的链接样式会泄漏到后续文本。加粗 `**` 要求前面空格，中文不符合。需绕过 lexer 限制。

## Decisions

1. **#9**: style 18 改为黑色无下划线 (30,30,30)，不做链接视觉区分
2. **#17**: 正则 `==(.{2,}?)==` 替代 `==(.+?)==`，最小内容 2 字符
3. **#18**: 新增 `_setup_bold_indicator()` + `_apply_bold()`，用 PlainIndicator + 粗体 QFont 渲染 `**text**`，与 `_apply_highlights` 共用 300ms timer
