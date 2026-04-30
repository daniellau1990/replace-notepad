# Version History

> 每个版本可通过 `git checkout <tag>` 回退
> 当前最新: `git checkout v0.3.1`

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
