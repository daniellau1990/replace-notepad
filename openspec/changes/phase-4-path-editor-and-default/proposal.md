## Why

状态栏路径需要可点击修改，方便用户切换默认保存目录。需要支持将 LiteNotepad 设为 Windows 默认编辑器。

## What Changes

- ClickablePathWidget 左键点击弹出目录选择对话框
- 文件菜单新增"设为默认编辑器"，写入注册表

## Capabilities

### New Capabilities

- `default-editor`: 将 LiteNotepad 注册为 .md/.txt 的默认打开程序

### Modified Capabilities

- `status-bar`: ClickablePathWidget 支持点击修改路径
