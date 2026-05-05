## MODIFIED Requirements

### Requirement: Line spacing

编辑器 SHALL 使用紧凑行间距，行高等于字体像素高度，匹配 Windows 记事本的排版密度。

#### Scenario: Text appears with compact line spacing

- **WHEN** 编辑器显示多行文本
- **THEN** 行间距与 Windows 记事本一致

### Requirement: Whitespace visibility

编辑器 SHALL 不显示空格和制表符的可见标记。

#### Scenario: Typing spaces on empty line

- **WHEN** 用户在空行连续输入空格
- **THEN** 空格不显示灰色背景或任何可见标记
