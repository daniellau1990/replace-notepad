## Why

关闭标签页时弹出的保存确认对话框打断了用户的编辑流，每次都要多点击一次。既然状态栏已经显示了保存目标路径，这个确认步骤是不必要的摩擦。改为静默自动保存，同时加入保存失败时的 fallback 机制保护数据不丢失。

## What Changes

- 关闭标签页（Ctrl+W / 点 X）不再弹出保存确认对话框，直接保存到状态栏路径
- 关闭整个窗口时同样静默保存所有脏标签，不再逐个弹框
- 保存失败时自动 fallback 到 `Documents\Notes\` 目录，同名文件自动递增编号
- 状态栏提示 fallback 路径

## Capabilities

### New Capabilities

- `silent-close-save`: 关闭标签时静默保存 + 保存失败 fallback 到默认目录并自动换名

### Modified Capabilities

- `tab-management`: Tab Close 行为变更 — 从弹框确认改为静默自动保存，关闭后记录 `_prev_editor_path` 的约束保持不变

## Impact

- `notepad/src/app.py`: `_confirm_save_and_close()` 替换为 `_auto_save_and_close()`，去掉 QMessageBox 弹框，加入 fallback 保存逻辑
