## ADDED Requirements

### Requirement: Silent save on tab close

关闭标签页时，系统 SHALL 自动保存编辑器内容到已知路径，不弹出确认对话框。

#### Scenario: Close dirty tab with known path

- **WHEN** 用户关闭一个有路径且内容已修改的标签
- **THEN** 系统直接保存到原路径并关闭标签，不弹出对话框

#### Scenario: Close dirty unnamed tab

- **WHEN** 用户关闭一个无路径且内容已修改的标签
- **THEN** 系统自动保存到 `Documents\Notes\{默认名}.md` 并关闭标签，不弹出对话框

#### Scenario: Close clean tab

- **WHEN** 用户关闭一个未修改的标签
- **THEN** 系统直接关闭标签，不执行保存操作

### Requirement: Fallback save on failure

保存到目标路径失败时，系统 SHALL 自动 fallback 到 `%USERPROFILE%\Documents\Notes\` 目录，同名文件自动递增编号。

#### Scenario: Original path save fails

- **WHEN** 保存到原路径时发生 OSError
- **THEN** 系统自动保存到 `Documents\Notes\{原文件名}.md`，若同名存在则递增编号（如 `file2.md`, `file3.md`）
- **AND** 状态栏显示 "原路径保存失败，已保存到 {fallback_path}"

#### Scenario: Both original and fallback fail

- **WHEN** 原路径和 fallback 目录均保存失败
- **THEN** 系统弹出 QMessageBox.warning 告知用户，并阻止标签关闭
