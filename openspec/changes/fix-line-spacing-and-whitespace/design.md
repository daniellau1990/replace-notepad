## Context

editor.py `_setup_caret()` 已设 setExtraAscent(0)，`_setup_auto_indent()` 已关 setIndentationGuides。但行间距仍大、空格仍灰底。

## Decisions

1. `_setup_caret()` 追加 `SCI_SETLINESPACING` = 字体 metrics 高度，压缩行间额外 gap
2. `_setup_auto_indent()` 追加 `SCI_SETVIEWWS(SCWS_INVISIBLE)`，关闭空格/制表符可见标记
