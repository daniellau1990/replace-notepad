# AutoSave

## Behavior
- 30 秒无操作后自动保存（debounce timer, single shot）
- 保存直接写入原文件，不创建 .tmp 或备份文件
- `textChanged` 信号触发 `mark_dirty()` → 启动 timer

## Unnamed File Handling
- 无路径时，自动保存到 `%USERPROFILE%\Documents\Notes\`
- 文件名来源：`filename_candidate()`（未命名→默认名，已保存→basename 主干）
- 文件名经 `_sanitize_filename()` 过滤非法字符后加 `.md` 后缀
- 保存后调用 `mark_clean()` + `_update_tab_title()` 同步状态

## Manual Save (Ctrl+S)
- 有路径：直接保存
- 无路径：弹出保存对话框

## Status Bar Feedback
- 保存成功：状态栏显示 "已保存 xxx.md"（3 秒闪现）
- 保存失败：状态栏显示 "保存失败: {error}"

## Constraints
- 默认保存目录需自动创建（`os.makedirs(exist_ok=True)`）
- 仅当 editor 存在时执行 mark_clean / update_tab_title
