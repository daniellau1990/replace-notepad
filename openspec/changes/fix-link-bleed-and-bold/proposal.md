## Why

三个编辑器渲染缺陷：图片路径使后续文字全变蓝色，`== ==` 误触发绿底漂移，中文后 `**` 无法加粗。

## What Changes

- 链接样式改为普通黑色，消除颜色泄漏
- 高亮正则要求至少 2 字符内容，跳过 `== ==` 
- `**text**` 改用 indicator 渲染粗体，绕过 lexer 限制

## Capabilities

### Modified Capabilities

- `markdown-editor`: 链接样式中性化，高亮匹配更严格，加粗通过 indicator 实现
