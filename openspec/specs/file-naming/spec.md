# File Naming

## Sanitization (`_sanitize_filename`)
- **删除**（不是替换为 `_`）以下所有字符：
  - OS 非法字符：`<>:"/\|?*`
  - MD 格式字符：`#*_~`[]()`
- 截断到 40 字符
- 两端空格清除
- 空结果回退为 `"未命名"`

## Filename Candidate (`filename_candidate`)
- 未命名文件：返回默认名（如 `"未命名1"`），不含扩展名
- 已保存文件：返回 `os.path.splitext(basename)[0]`（文件名主干）
- **与首行内容无关**（首行 ≠ 文件名）

## Tab Title (`_update_tab_title`)
- 未命名文件：`"{默认名}.md"` — 始终使用默认名，不与首行同步
- 已保存文件：`os.path.basename(path)` — 真实文件名
- 脏标记：修改未保存时追加 `" ●"`
- 防重复扩展名：使用 `os.path.splitext(stem)[0] + ".md"`

## Tab Rename (`_on_double_click` + `_on_rename_requested`)
- 重命名框始终显示文件名主干（无条件 `os.path.splitext`），不含扩展名
- 未命名文件：更新 `_default_names`，sanitize 后生效
- 已保存文件：`os.rename()` 重命名磁盘文件
- 输入自动经 `_sanitize_filename` 过滤非法字符

## Constraints
- 首行内容完全不影响文件名/标签/状态栏
