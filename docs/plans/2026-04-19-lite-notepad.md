# LiteNotepad Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Build a lightweight cross-platform notepad replacement with auto-save, line numbers, bold/italic, and Markdown syntax highlighting. Target: ~5MB executable per platform.

**Architecture:**
- Tauri 1.x with minimal frontend (single HTML file + vanilla JS)
- No React, no CodeMirror — use native WebView text rendering
- Line numbers via CSS/JS
- Syntax highlighting via lightweight custom regex (no heavy library)
- Auto-save via Tauri FS API with debounce

**Tech Stack:**
- Tauri 1.x (Rust backend)
- Vanilla HTML/CSS/JS frontend
- highlight.js (minimal, only MD patterns) or custom regex highlighter

---

## Task 1: Create SPEC.md

**Files:**
- Create: `SPEC.md`

**Step 1: Write specification**

```markdown
# LiteNotepad - Specification

## Overview
A lightweight cross-platform notepad replacement built with Tauri.
Target: <5MB executable, <100ms startup time.

## Features

### Core Editor
- [ ] Plain text editing with monospace font
- [ ] Line numbers (left gutter, synced scroll)
- [ ] Word wrap enabled by default
- [ ] Cursor position display (Ln X, Col Y)

### Formatting
- [ ] Bold text (Ctrl+B) — wrap selection with **
- [ ] Italic text (Ctrl+I) — wrap selection with *
- [ ] Visual rendering of bold/italic in editor

### File Operations
- [ ] Open .txt and .md files via native dialog
- [ ] Save / Save As via native dialog
- [ ] Remember last opened directory

### Auto-Save
- [ ] Auto-save every 60 seconds if content changed
- [ ] Visual indicator when auto-save occurs
- [ ] No data loss on crash

### Syntax Highlighting (minimal)
- [ ] Markdown headers (# ## ### etc.) — larger/bold
- [ ] Markdown code blocks (```) — monospace background
- [ ] Bold (**text**) and Italic (*text*)
- [ ] URLs — underlined blue

### Status Bar
- [ ] Current file name (or "Untitled")
- [ ] Dirty indicator (*)
- [ ] Line count, character count
- [ ] Auto-save status

## UI Design
- Single window, no tabs
- Menu bar: File, Edit, Format, Help
- Optional formatting toolbar (B, I buttons)
- Status bar at bottom
- Native window controls

## Platform Support
- Windows (.exe)
- Linux (AppImage)
- macOS (.app)
```

**Step 2: Commit**

```bash
git add SPEC.md
git commit -m "docs: add LiteNotepad specification"
```

---

## Task 2: Create Project Structure

**Files:**
- Create: `src/main.rs`
- Create: `src-tauri/src/commands.rs`
- Create: `src/index.html`
- Create: `src/style.css`
- Create: `src/editor.js`

**Step 1: Set up Tauri main.rs**

```rust
#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

mod commands;

use tauri::Manager;

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            commands::open_file,
            commands::save_file,
            commands::get_file_size,
        ])
        .setup(|app| {
            let window = app.get_window("main").unwrap();
            window.set_title("LiteNotepad").ok();
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

**Step 2: Create commands.rs**

```rust
use std::fs;
use std::path::PathBuf;
use tauri::command;

#[command]
pub fn open_file(path: String) -> Result<String, String> {
    fs::read_to_string(&path).map_err(|e| e.to_string())
}

#[command]
pub fn save_file(path: String, content: String) -> Result<(), String> {
    fs::write(&path, &content).map_err(|e| e.to_string())
}

#[command]
pub fn get_file_size(path: String) -> Result<u64, String> {
    fs::metadata(&path).map(|m| m.len()).map_err(|e| e.to_string())
}
```

**Step 3: Create minimal index.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>LiteNotepad</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div id="app">
        <div id="toolbar">
            <button id="btn-bold" title="Bold (Ctrl+B)">B</button>
            <button id="btn-italic" title="Italic (Ctrl+I)">I</button>
        </div>
        <div id="editor-container">
            <div id="line-numbers"></div>
            <textarea id="editor" spellcheck="false"></textarea>
        </div>
        <div id="statusbar">
            <span id="filename">Untitled</span>
            <span id="info"></span>
            <span id="autosave-status"></span>
        </div>
    </div>
    <script src="editor.js" type="module"></script>
</body>
</html>
```

**Step 4: Commit**

```bash
git add src/main.rs src-tauri/src/commands.rs src/index.html src/style.css src/editor.js
git commit -m "feat: initial LiteNotepad structure"
```

---

## Task 3: Implement Line Numbers

**Files:**
- Modify: `src/style.css`
- Modify: `src/editor.js`

**Step 1: Add CSS for line numbers gutter**

```css
#editor-container {
    display: flex;
    height: 100vh;
    background: #1e1e1e;
}

#line-numbers {
    width: 50px;
    background: #252526;
    color: #858585;
    text-align: right;
    padding: 10px 5px;
    font-family: Consolas, monospace;
    font-size: 14px;
    line-height: 1.5;
    overflow: hidden;
    user-select: none;
}

#editor {
    flex: 1;
    background: #1e1e1e;
    color: #d4d4d4;
    border: none;
    padding: 10px;
    font-family: Consolas, monospace;
    font-size: 14px;
    line-height: 1.5;
    resize: none;
    outline: none;
}
```

**Step 2: Implement line number sync in editor.js**

```javascript
const editor = document.getElementById('editor');
const lineNumbers = document.getElementById('line-numbers');

function updateLineNumbers() {
    const lines = editor.value.split('\n').length;
    let html = '';
    for (let i = 1; i <= lines; i++) {
        html += i + '\n';
    }
    lineNumbers.textContent = html;
}

editor.addEventListener('input', updateLineNumbers);
editor.addEventListener('scroll', () => {
    lineNumbers.scrollTop = editor.scrollTop;
});

// Initialize
updateLineNumbers();
```

**Step 3: Commit**

```bash
git add src/style.css src/editor.js
git commit -m "feat: implement line numbers"
```

---

## Task 4: Implement Bold/Italic Formatting

**Files:**
- Modify: `src/editor.js`

**Step 1: Add wrapSelection function**

```javascript
function wrapSelection(before, after = before) {
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const text = editor.value;
    const selected = text.substring(start, end);

    const newText = text.substring(0, start) + before + selected + after + text.substring(end);
    editor.value = newText;

    // Restore selection
    editor.selectionStart = start + before.length;
    editor.selectionEnd = end + before.length;
    editor.focus();
    updateLineNumbers();
    highlightMarkdown();
}

// Bold: Ctrl+B
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'b') {
        e.preventDefault();
        wrapSelection('**');
    }
    if (e.ctrlKey && e.key === 'i') {
        e.preventDefault();
        wrapSelection('*');
    }
});

// Toolbar buttons
document.getElementById('btn-bold').addEventListener('click', () => wrapSelection('**'));
document.getElementById('btn-italic').addEventListener('click', () => wrapSelection('*'));
```

**Step 2: Commit**

```bash
git commit -m "feat: implement bold/italic formatting"
```

---

## Task 5: Implement Syntax Highlighting

**Files:**
- Modify: `src/style.css`
- Modify: `src/editor.js`

**Step 1: Add highlighting styles**

```css
/* Syntax highlighting classes */
.md-header { color: #569cd6; font-weight: bold; }
.md-bold { color: #ce9178; font-weight: bold; }
.md-italic { color: #ce9178; font-style: italic; }
.md-code { background: #2d2d2d; color: #ce9178; }
.md-link { color: #4ec9b0; text-decoration: underline; }
```

**Step 2: Create overlay highlighter**

```javascript
const highlightLayer = document.createElement('pre');
highlightLayer.id = 'highlight-layer';
highlightLayer.style.cssText = 'position:absolute;top:0;left:50px;right:0;bottom:0;padding:10px;margin:0;font-family:Consolas,monospace;font-size:14px;line-height:1.5;pointer-events:none;overflow:hidden;white-space:pre-wrap;word-wrap:break-word;';
document.getElementById('editor-container').appendChild(highlightLayer);
editor.style.color = 'transparent';
editor.style.caretColor = 'white';

function escapeHtml(text) {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}

function highlightMarkdown() {
    const text = editor.value;
    let html = escapeHtml(text);

    // Headers
    html = html.replace(/^(#{1,6}\s.*)$/gm, '<span class="md-header">$1</span>');
    // Bold
    html = html.replace(/(\*\*[^*]+\*\*)/g, '<span class="md-bold">$1</span>');
    // Italic
    html = html.replace(/(\*[^*]+\*)/g, '<span class="md-italic">$1</span>');
    // Code blocks
    html = html.replace(/(```[\s\S]*?```)/g, '<span class="md-code">$1</span>');
    // Inline code
    html = html.replace(/(`[^`]+`)/g, '<span class="md-code">$1</span>');
    // Links
    html = html.replace(/(\[.*?\]\(.*?\))/g, '<span class="md-link">$1</span>');

    highlightLayer.innerHTML = html + '\n';
    highlightLayer.scrollTop = editor.scrollTop;
    highlightLayer.scrollLeft = editor.scrollLeft;
}
```

**Step 3: Sync scroll**

```javascript
editor.addEventListener('scroll', () => {
    highlightLayer.scrollTop = editor.scrollTop;
    highlightLayer.scrollLeft = editor.scrollLeft;
});
```

**Step 4: Commit**

```bash
git commit -m "feat: implement markdown syntax highlighting"
```

---

## Task 6: Implement File Open/Save

**Files:**
- Modify: `src/editor.js`

**Step 1: Add Tauri invoke calls**

```javascript
const { invoke } = window.__TAURI__.core;
const { open, save } = window.__TAURI__.dialog;
const { getCurrentWindow } = window.__TAURI__.window;

let currentFilePath = null;

async function openFile() {
    const selected = await open({
        filters: [{
            name: 'Text Files',
            extensions: ['txt', 'md']
        }]
    });

    if (selected) {
        const content = await invoke('open_file', { path: selected });
        editor.value = content;
        currentFilePath = selected;
        updateFilename();
        updateLineNumbers();
        highlightMarkdown();
    }
}

async function saveFile() {
    if (!currentFilePath) {
        return saveFileAs();
    }
    await invoke('save_file', {
        path: currentFilePath,
        content: editor.value
    });
    updateFilename();
}

async function saveFileAs() {
    const path = await save({
        filters: [{
            name: 'Text Files',
            extensions: ['txt', 'md']
        }]
    });

    if (path) {
        currentFilePath = path;
        await invoke('save_file', { path, content: editor.value });
        updateFilename();
    }
}
```

**Step 2: Commit**

```bash
git commit -m "feat: implement file open/save"
```

---

## Task 7: Implement Auto-Save

**Files:**
- Modify: `src/editor.js`

**Step 1: Add auto-save logic**

```javascript
let autoSaveTimer = null;
let isDirty = false;
const AUTO_SAVE_INTERVAL = 60000; // 60 seconds

function scheduleAutoSave() {
    if (autoSaveTimer) clearTimeout(autoSaveTimer);
    if (isDirty && currentFilePath) {
        autoSaveTimer = setTimeout(async () => {
            await invoke('save_file', {
                path: currentFilePath,
                content: editor.value
            });
            isDirty = false;
            document.getElementById('autosave-status').textContent = 'Auto-saved';
            setTimeout(() => {
                document.getElementById('autosave-status').textContent = '';
            }, 2000);
        }, AUTO_SAVE_INTERVAL);
    }
}

editor.addEventListener('input', () => {
    isDirty = true;
    updateFilename();
    updateLineNumbers();
    highlightMarkdown();
    scheduleAutoSave();
});
```

**Step 2: Commit**

```bash
git commit -m "feat: implement auto-save"
```

---

## Task 8: Add Menu Bar

**Files:**
- Modify: `src/index.html`
- Modify: `src/editor.js`

**Step 1: Add menu HTML**

```html
<div id="menubar">
    <span class="menu-item" data-menu="file">File
        <div class="menu-dropdown">
            <div onclick="openFile()">Open...</div>
            <div onclick="saveFile()">Save</div>
            <div onclick="saveFileAs()">Save As...</div>
            <hr>
            <div onclick="getCurrentWindow().close()">Exit</div>
        </div>
    </span>
    <span class="menu-item" data-menu="edit">Edit
        <div class="menu-dropdown">
            <div onclick="document.execCommand('undo')">Undo</div>
            <div onclick="document.execCommand('redo')">Redo</div>
            <hr>
            <div onclick="document.execCommand('cut')">Cut</div>
            <div onclick="document.execCommand('copy')">Copy</div>
            <div onclick="document.execCommand('paste')">Paste</div>
            <div onclick="selectAll()">Select All</div>
        </div>
    </span>
</div>
```

**Step 2: Commit**

```bash
git commit -m "feat: add menu bar"
```

---

## Task 9: Update Status Bar

**Files:**
- Modify: `src/editor.js`

**Step 1: Add status updates**

```javascript
function updateFilename() {
    const name = currentFilePath
        ? currentFilePath.split(/[/\\]/).pop()
        : 'Untitled';
    document.getElementById('filename').textContent =
        isDirty ? name + ' *' : name;
}

function updateInfo() {
    const lines = editor.value.split('\n').length;
    const chars = editor.value.length;
    const sel = editor.selectionStart;
    const line = editor.value.substring(0, sel).split('\n').length;
    const col = sel - editor.value.lastIndexOf('\n', sel - 1);
    document.getElementById('info').textContent =
        `Ln ${line}, Col ${col} | ${chars} chars, ${lines} lines`;
}

editor.addEventListener('click', updateInfo);
editor.addEventListener('keyup', updateInfo);
```

**Step 2: Commit**

```bash
git commit -m "feat: update status bar with file info"
```

---

## Task 10: Build for All Platforms

**Step 1: Install Rust (if not present)**

```bash
# Linux/macOS
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Windows: Download from https://rustup.rs
```

**Step 2: Build commands**

```bash
# Windows
npm run build -- --target x86_64-pc-windows-msvc

# Linux
npm run build -- --target x86_64-unknown-linux-gnu

# macOS
npm run build -- --target aarch64-apple-darwin
```

**Step 3: Verify executables**

| Platform | Output |
|----------|--------|
| Windows | `src-tauri/target/x86_64-pc-windows-msvc/release/LiteNotepad.exe` |
| Linux | `src-tauri/target/x86_64-unknown-linux-gnu/release/litenotepad` |
| macOS | `src-tauri/target/aarch64-apple-darwin/release/LiteNotepad.app` |

**Step 4: Commit build config**

```bash
git add .
git commit -m "chore: add platform-specific build configs"
```

---

## Verification Steps

1. **Run dev mode:**
   ```bash
   npm run dev
   ```
   Verify: App opens, line numbers visible, typing works

2. **Open a .md file:**
   - Click File > Open
   - Select a markdown file
   - Verify syntax highlighting works

3. **Test auto-save:**
   - Make changes
   - Wait 60 seconds
   - Verify no data loss

4. **Build and run executable:**
   - Run `npm run build`
   - Execute the .exe/.app binary
   - Verify standalone operation
