# Version History

> 每个版本可通过 `git checkout <tag>` 回退
> 当前最新: `git checkout v0.3.6`

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
