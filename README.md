# replace-notepad

A lightweight Windows notepad replacement built with **Python 3.9 + PyQt6 + QScintilla**.

## Features

- Auto-save (30s debounce, Obsidian-style)
- Line numbers via QScintilla
- Markdown syntax highlighting
- Live Markdown preview (side-by-side, Ctrl+P toggle)
- Multi-tab editing (Ctrl+T / Ctrl+W)
- Bold formatting (Ctrl+B)
- Font zoom (Ctrl+Scroll)
- Find/replace bar
- UTF-8/GBK encoding detection
- Recent files list

## Quick Start

```bash
cd notepad
python -m venv .venv
.venv\Scripts\activate
pip install PyQt6 PyQt6-QScintilla markdown
python main.py
```

## Project Structure

```
notepad/
├── main.py              # Entry point
├── src/
│   ├── app.py           # Main window, menus, toolbar
│   ├── editor.py        # QScintilla editor with MD lexer
│   ├── tab_manager.py   # Multi-tab management
│   ├── md_preview.py    # Live Markdown preview
│   ├── autosave.py      # Auto-save timer
│   ├── file_handler.py  # File I/O, encoding detection
│   ├── find_replace.py  # Find/replace bar
│   └── settings.py      # QSettings persistence
└── tests/               # Unit tests
```

## Requirements

- Python 3.9+
- Windows 10+

