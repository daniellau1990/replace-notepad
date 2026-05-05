## Context

`_apply_font_size()` 只改了 editor 的 font，但 MarkdownLexer 每个 style 有独立字体大小，优先级更高。Indicator alpha=80 叠在白色背景上几乎不可见。

## Goals / Non-Goals

**Goals:** 字体对话框生效、`==text==` 显示绿色高亮
**Non-Goals:** 不改变 lexer 其他样式、不改变高亮颜色

## Decisions

1. `MarkdownLexer.update_font_size(size)` — 遍历 style 0-19，逐个更新字体大小
2. `_apply_font_size()` 追加 `lexer.update_font_size(size)` 调用
3. Indicator alpha 80→160
4. `clearIndicatorRange` 的 end_pos 用 `self.lineLength(self.lines()-1)` 而非 `0`
