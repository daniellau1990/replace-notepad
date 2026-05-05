## MODIFIED Requirements

### Requirement: Font size setting

系统 SHALL 在用户通过格式→字体对话框修改字体大小后，将新大小应用到所有编辑器标签页及对应的 Markdown 语法高亮样式。

#### Scenario: User changes font size via dialog

- **WHEN** 用户打开格式→字体对话框并选择新字体大小
- **THEN** 所有打开标签页的编辑器和 lexer 样式均使用新字体大小

### Requirement: Highlight rendering

系统 SHALL 对 `==text==` 包裹的文本渲染可见的绿色高亮背景。

#### Scenario: User types highlight markup

- **WHEN** 用户输入 `==highlight==`
- **THEN** 该文本显示绿色高亮背景
