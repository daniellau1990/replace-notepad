## Why

两个 bug 导致核心编辑功能不可用：格式→字体调节滑块实际不改变编辑器字体大小，`==text==` 高亮标记完全不可见。都是 1-2 行的修复。

## What Changes

- 字体对话框选择新大小后，实际应用到编辑器和 lexer 所有 style
- `==text==` 高亮指示器变得更可见，清除范围修正

## Capabilities

### Modified Capabilities

- `markdown-editor`: 字体大小设置现在对 lexer 所有样式生效；高亮 indicator 可见性修复
