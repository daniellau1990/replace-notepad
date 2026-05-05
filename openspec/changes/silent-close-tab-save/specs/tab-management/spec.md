## MODIFIED Requirements

### Requirement: Tab Close

- `Ctrl+W`：关闭当前标签
- 如有未保存修改，自动保存到状态栏路径（不弹对话框）
- 无路径文件自动保存到默认目录（`Documents\Notes\{默认名}.md`）
- 保存失败时 fallback 到 `Documents\Notes\`，同名自动递增编号
- 关闭后记录 `_prev_editor_path`（用于下次保存对话框定位）
