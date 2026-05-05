## Context

ClickablePathWidget 只显示路径无法交互。需加 mousePressEvent。注册表操作只在 HKCU 下，不需要管理员权限。

## Decisions

1. **#5**: mousePressEvent → QFileDialog.getExistingDirectory → 更新 settings + 刷新显示
2. **#13**: 文件菜单加 action → 写 HKCU\Software\Classes\.md\OpenWithProgids + HKCU\Software\Classes\LiteNotepad.md\
3. **#15**: 代码无限制，跳过
