# Version History

> 每个版本可通过 `git checkout <tag>` 回退
> 当前最新: `git checkout v0.3.13`

## v0.3.13 (2026-05-06) [`git tag: v0.3.13`]
- **Phase 4 新功能**:
  1. 状态栏路径左键单击弹出目录选择对话框，修改默认保存路径
  2. 文件菜单新增"设为默认编辑器"——写入 HKCU 注册表关联 .md/.txt
  3. 确认标签页无硬性数量限制
- CLAUDE.md 更新: 日志记录规则、苏格拉底五问调试法、测试原则

## v0.3.12 (2026-05-05) [`git tag: v0.3.12`]
- **Phase 3 编辑器缺陷修复**:
  1. 修复链接样式泄漏——style 18 蓝色+下划线改为中性黑色
  2. 修复绿底漂移——高亮正则改为 `==(.{2,}?)==` 跳过 `== ==` 误匹配
  3. 修复中文加粗失效——`_apply_bold()` 用 SCI_STARTSTYLING style 2 绕过 lexer 限制
- 更新测试: `test_link_is_blue` → `test_link_is_neutral`

## v0.3.11 (2026-05-05) [`git tag: v0.3.11`]
- **Phase 2 排版修复**:
  1. 行间距压缩——SCI_SETLINESPACING 设为字体像素高度，匹配记事本紧凑行距
  2. 空格灰色背景修复——SCI_SETVIEWWS=0 关闭空白字符可见标记

## v0.3.10 (2026-05-05) [`git tag: v0.3.10`]
- **Phase 1 核心修复**:
  1. 字体大小对话框生效——MarkdownLexer 新增 `update_font_size()`，_apply_font_size 同步更新全部 20 个 style
  2. 高亮 `==text==` 可见——indicator alpha 从 80 提升到 160，修正 clearIndicatorRange 边界

## v0.3.9 (2026-05-05) [`git tag: v0.3.9`]
- **关闭标签静默自动保存**:
  - `_confirm_save_and_close` 替换为 `_auto_save_and_close`，关闭标签不弹确认对话框
  - 新增 `_save_with_fallback`——保存失败自动 fallback 到 Documents\Notes\ 并递增编号
  - 关闭窗口同样静默保存所有脏标签

## v0.3.8 (2026-05-03) [`git tag: v0.3.8`]
- **Guardrail 工作流强制执行**:
  - 新增 `.claude/hooks/workflow_check.py` — PreToolUse hook 脚本，检查 `docs/plans/` 当日计划文件
  - 重构 `CLAUDE.md` — MANDATORY WORKFLOW 置于文件顶部，含 GATE 检查点和 Quick Compliance Check
  - 新增 `settings.local.json` hooks — Write|Edit 守卫 + git commit 守卫
  - 新增文档 `docs/2026-05-03-Guardrail.md` / `Harness.md` / `Guardrail-vs-Harness.md`
- 白名单路径始终放行：`docs/**`、`Version.md`、`CLAUDE.md`、`*.bat`、`.claude/**`

## v0.3.7 (2026-05-03) [`git tag: v0.3.7`]
- **12 项需求合集**:
  1. 行间距缩小 (`setExtraAscent/Descent(0)`)
  2. 空格灰底修复 (关闭 indentation guides)
  3. 水平滚动条移除 (word wrap + SCI_SETHSCROLLBAR)
  4. Ctrl+S 直接保存到默认路径，不弹对话框
  5. 状态栏路径右击可修改默认保存目录
  6. 文件名不过滤 `_` 下划线
  7. 格式→字体：字号调节对话框 (SpinBox+Slider+预览)
  8. 格式→自动换行：checkable 切换
  9. 图片拖入编辑区插入 `![](path)` Markdown
  10. 快捷键菜单（展示常用快捷键）
  11. 版本菜单（显示 v0.3.7）
  12. `==高亮==` 语法（绿色 RoundBox indicator）
- bat 启动脚本优化：`pythonw.exe` + `start ""` 静默启动

## v0.3.6 (2026-04-30) [`git tag: v0.3.6`]
- **修复（根因定位）**: 保存后重命名 .md 递增 bug — 根因是 `_on_double_click` 只对未命名文件剥离扩展名，保存后的文件重命名框展示带 `.md` 的完整文件名，导致扩展名叠加
- 修复方案: `os.path.splitext` 改为**无条件**剥离，保存/未保存统一行为
- 测试: 57 项全部通过（+2 项防御性测试）
- **修复**: `run_app.bat` / `note_pad_run.bat` CMD 窗口问题 — 移除 `chcp 65001`（导致命令错误分词），改用 `pythonw.exe` + `start ""` 静默启动，双击不再驻留 CMD 窗口

## v0.3.5 (2026-04-30) [`git tag: v0.3.5`]

**用户反馈修复：**
- 修复: 新建文件首行去掉 `#` 号，直接显示 `未命名N`
- 修复: 自动保存后状态栏一直显示"未保存"→ `_do_save` 缺少 `mark_clean` 调用
- 修复: 双击重命名产生 `.md.md.md` 重复叠加 → `os.path.splitext` 替换不健壮的 `replace(".md","")`
- 新增: 状态栏路径标签支持鼠标选中复制（IBeam 光标 + 文本可选）
- 测试: 55 项全部通过
- **用户验证（2026-04-30）：四个 bug 全部完美解决，自动保存+路径显示+实时更新保存状态均实现 ✅**
- **遗留问题：保存后重命名标签，.md 再次开始递增（保存前正常）**

## v0.3.4 (2026-04-30) [`git tag: v0.3.4`]
- 修复: `_sanitize_filename` 将 OS 非法字符**删除**而非替换为 `_`（`**\\wode` → `wode` 而非 `__wode`）
- 重构: 标签标题与首行内容解耦 — 标签始终显示文件名（未命名→`未命名N.md`，已保存→真实文件名）
- 重构: `filename_candidate` 改为返回默认名（未命名文件）或文件名主干（已保存文件），不再从首行提取
- 优化: 状态栏显示完整保存路径 + 彩色保存状态（绿=已保存，橙=未保存）
- 修复: 双击标签重命名时自动过滤非法字符
- 修复: 未命名文件重命名框显示不带 `.md` 的名称（避免用户误改扩展名）
- 测试: 55 项全部通过（新增 test_sanitize.py 24项 + test_tab_title.py 7项）

## v0.3.3 (2026-04-30) [`git tag: v0.3.3`]
- 修复: 新建文件首行空白 → 自动写入 `# 未命名N`，标签名与首行一致
- 修复: 状态栏始终显示 `(未保存)` → 显示预期自动保存路径 `Documents/Notes/xxx.md`
- 修复: 自动保存 30 秒从未触发 → `textChanged` 连接到 `AutoSave.mark_dirty()`
- 修复: `status_callback` 为空操作 → 自动保存成功后在状态栏显示提示
- 修复: 首行 MD 格式字符 `**` `_` `~` 等污染文件名 → 自动过滤为合法文件名
- 优化: 未命名文件窗口标题从 `LiteNotepad` 改为 `未命名N - LiteNotepad`

## v0.3.2 (2026-04-30) [`git tag: v0.3.2`]
- 修复: `*斜体*` 改为酒红色（Burgundy）显示，强调内容更醒目
- 修复: 引用文字灰色斜体渲染优化
- 修复: 为全部 QsciLexerMarkdown 样式优化字体/颜色定义
- 注意: PyQt6 QScintilla 绑定层限制，样式定义已保存但编辑器内文本样式应用有限
- 测试: 22 项全部通过

### 用户反馈
- ✓ `**加粗**` 和 `*斜体酒红色*` 效果满意，当前方案够用
- ✓ 无需标题大字号功能，保持现状即可
- → 后续升级方向：如果需要完整着色可换 QTextEdit + QSyntaxHighlighter

## v0.3.1 (2026-04-30) [`git tag: v0.3.1`]
- 修复: 为全部 19 个 QsciLexerMarkdown 样式设置字体、前景色和背景色
- 功能: `**加粗**` 和 `*斜体*` 行内样式正常渲染
- 功能: 行内 `` `代码` `` 红字灰底显示
- 功能: 引用文字（`>`）灰色斜体
- 功能: 代码块灰底
- 注意: `#`/`##`/`###` 标记符号显示为对应标题字号，但标题文字因 PyQt6 QScintilla 绑定层限制保持默认大小

## v0.1.0 (2026-04-28) [`git tag: v0.1.0`](204cd3e)
- Initial implementation: Python + PyQt6 + QScintilla
- Feature: Multi-tab editor with line numbers
- Feature: Markdown syntax highlighting (QsciLexerMarkdown)
- Feature: Auto-save (30s debounce, Obsidian-style)
- Feature: Ctrl+B bold toggle
- Feature: Ctrl+Scroll zoom
- Feature: Markdown live preview (Ctrl+P toggle)
- Feature: Find/Replace bar (Ctrl+F)
- Feature: File open/save with UTF-8/GBK detection
- Feature: Recent files list
- Feature: Font zoom persistence via QSettings
- Default save dir: ~/Documents/Notes/

## v0.3.0 (2026-04-30) [`git tag: v0.3.0`](9b89030)
- Feature: Obsidian 风格统一界面，移除分栏预览面板
- Feature: 自定义 MarkdownLexer 实现编辑器内 WYSIWYG 样式（H1=22pt, H2=18pt, 代码块灰底, 链接蓝色）
- Feature: 智能状态栏（左侧永久行/列 + 右侧可编辑保存路径）
- Feature: 苹果式简洁设计（Fusion 样式 + 极简 QSS）
- Remove: MarkdownPreview 独立预览面板
- Remove: View 菜单（Ctrl+P 预览切换）

## v0.2.0 (2026-04-29) [`git tag: v0.2.0`](8d5b029)
- Feature: First line auto-becomes filename (Obsidian-style, "未命名文件N" default)
- Feature: Open named files inserts `# filename` as bold heading
- Feature: Save confirmation dialog on close (Save/Cancel, no Discard)
- Feature: Double-click tab title to rename file
- Feature: Ctrl+S on unnamed file shows save dialog
- Feature: Tab title updates in real-time with first line text
- Refactor: Per-editor dirty state tracking in TabManager
- Fix: Save dialog fallback uses previous tab's path, not current tab's path
