# Version History

## v0.1.0 (2026-04-28)
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

## v0.2.0 (2026-04-29)
- Feature: First line auto-becomes filename (Obsidian-style, "未命名文件N" default)
- Feature: Open named files inserts `# filename` as bold heading
- Feature: Save confirmation dialog on close (Save/Cancel, no Discard)
- Feature: Double-click tab title to rename file
- Feature: Ctrl+S on unnamed file shows save dialog
- Feature: Tab title updates in real-time with first line text
- Refactor: Per-editor dirty state tracking in TabManager
- Fix: Save dialog fallback uses previous tab's path, not current tab's path
