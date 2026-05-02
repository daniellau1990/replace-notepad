# Status Bar

## Layout
- 左侧：行/列信息（`"第 N 行，第 M 列 | N 行"`），500ms 刷新
- 右侧：`ClickablePathWidget` + 查找替换栏（默认隐藏）

## ClickablePathWidget
- 已保存文件：绿色 `"已保存 — "` + 完整路径
- 未保存文件：橙色 `"未保存 — "` + 预期保存路径（`DEFAULT_DIR/{name}.md`）
- 无文件：`"(无文件)"`
- 路径文本使用 IBeam 光标，支持鼠标选中复制
- ToolTip 显示完整路径

## Save Status Refresh
- 500ms 定时器调用 `_update_path_display`
- 自动保存后通过 `mark_clean` → `is_dirty()=False` → 显示"已保存"
- 编辑后 `is_dirty()=True` → 显示"未保存"

## Constraints
- 颜色区分：`#34c759`（绿/已保存）、`#ff9500`（橙/未保存）
