## ADDED Requirements

### Requirement: Set as default editor

系统 SHALL 通过菜单操作将 LiteNotepad 注册为 .md 和 .txt 文件的默认打开程序。

#### Scenario: User clicks set as default

- **WHEN** 用户点击"文件→设为默认编辑器"
- **THEN** 注册表写入关联信息，.md/.txt 文件默认用 LiteNotepad 打开
