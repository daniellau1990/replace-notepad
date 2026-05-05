## MODIFIED Requirements

### Requirement: Link style

链接样式 SHALL 使用普通黑色文字，不使用蓝色或下划线，防止样式泄漏影响后续文本。

#### Scenario: Image path inserted

- **WHEN** 拖入图片插入 `![](path.png)`
- **THEN** 路径文字为普通黑色，后续文字不受影响

### Requirement: Highlight matching

高亮检测 SHALL 要求 `==` 之间至少 2 个字符，避免 `== ==` 等误匹配。

#### Scenario: == == literal text

- **WHEN** 文档包含 `== ==`（空格分隔）
- **THEN** 不触发高亮渲染

### Requirement: Bold rendering

系统 SHALL 对 `**text**` 包裹的文本渲染粗体效果，无论前面是中文还是其他字符。

#### Scenario: Chinese text before bold marker

- **WHEN** 文档包含 `文字**加粗**内容`
- **THEN** "加粗" 二字显示为粗体
