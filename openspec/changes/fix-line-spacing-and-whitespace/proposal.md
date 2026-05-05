## Why

QScintilla 默认行间距比 Windows 记事本大，且连续空格显示灰色背景标记。两个问题影响排版一致性。

## What Changes

- 行间距压缩到字体像素高度（SCI_SETLINESPACING）
- 关闭空白字符可见性（SCI_SETVIEWWS = SCWS_INVISIBLE）

## Capabilities

### Modified Capabilities

- `markdown-editor`: 行间距更紧凑匹配记事本，空格不再显示灰色背景
