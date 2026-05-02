# Markdown Editor

## Core
- QScintilla 编辑器 + QsciLexerMarkdown C++ 词法分析器
- 行号边栏（40px 宽，灰色）
- Consolas 11pt 默认字体
- 4 空格 Tab 宽度，自动缩进

## Syntax Highlighting
- **粗体** `**text**`：黑色粗体
- *斜体* `*text*`：酒红色斜体（#B22222）
- ~~删除线~~ `~~text~~`：灰色删除线
- `行内代码`：红字灰底
- 链接 `[text](url)`：蓝色下划线
- 标题 `# ~ ######`：不同字号（22pt~11pt）
- 代码块：灰底
- 引用 `>`：灰色斜体

## Keyboard Shortcuts
- `Ctrl+B`：切换粗体（选中文本包裹/去除 `**`）
- `Ctrl+Scroll`：字体缩放（zoomIn/zoomOut）

## Limitations
- QsciLexerMarkdown 是 C++ 内置 lexer，不支持自定义正则扩展
- 非标准 MD 语法（如 `==高亮==`）需用 Indicator 机制实现
