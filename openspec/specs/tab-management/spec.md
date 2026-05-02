# Tab Management

## Tab Creation
- `Ctrl+T`：新建标签页
- 新建未命名文件：首行写入 `"{默认名}\n\n"`（不含 `#`），标签显示 `{默认名}.md`
- 打开文件：标签显示 `os.path.basename(path)`
- 计数器独立递增（`未命名1, 未命名2, ...`）

## Tab Close
- `Ctrl+W`：关闭当前标签
- 如有未保存修改，弹出保存确认对话框
- 关闭后记录 `_prev_editor_path`（用于下次保存对话框定位）

## Tab Switch
- 切换标签时记录上一标签的文件目录

## Double-Click Rename
- 弹出 QLineEdit 编辑框
- 显示文件名主干（无扩展名），全选
- 确认后 emit `rename_requested` 信号

## First Line Heading
- 打开 .md 文件时，如首行不是 `# ` 开头，自动插入 `# {filename}` 标题
- 未命名文件不执行此逻辑

## Constraints
- 首行内容变更不触发标签标题变更
- 标签标题始终反映文件名，不是内容
