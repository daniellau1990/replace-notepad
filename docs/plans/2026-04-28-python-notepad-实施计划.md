# Python 记事本 — 实施计划

## 技术栈

- **Python 3.9** + **PyQt6** + **QScintilla**
- Markdown 渲染：`markdown` 库 (已安装 v3.9) + `QTextBrowser`
- 打包：`PyInstaller` → 单个 .exe

## 项目结构

```
D:\AIAGENT应用\replace_txt\notepad\
├── .venv/                   # 虚拟环境（所有依赖安装在此）
├── main.py                  # 入口
├── requirements.txt         # PyQt6, PyQt6-QScintilla, markdown
├── src/
│   ├── __init__.py
│   ├── app.py               # QMainWindow 主窗口（菜单、工具栏、状态栏）
│   ├── editor.py            # QScintilla 编辑器封装（行号、高亮、字体）
│   ├── tab_manager.py       # QTabWidget 多标签管理
│   ├── md_preview.py        # Markdown 实时预览面板（QSplitter 分栏）
│   ├── autosave.py          # QTimer 自动保存逻辑
│   ├── file_handler.py      # 文件读写（TXT / MD）
│   ├── find_replace.py      # 查找替换对话框
│   └── settings.py          # 字体大小、颜色主题等持久化配置
└── resources/
    └── icons/               # 工具栏图标（可选）
```

## 核心功能实现

### 1. 编辑器主体 (`editor.py`)
- 继承 `QsciScintilla`，封装所有编辑功能
- **行号**：`setMarginLineNumbers(0, True)` 自带
- **语法高亮**：MD 文件用 `QsciLexerMarkdown`，TXT 无高亮
- **加粗**：`Ctrl+B` 在选中文字两端加 `**text**`，Markdown 模式下预览渲染
- **字体缩放**：`Ctrl+滚轮` 实时调整 `zoomIn()/zoomOut()`
- **缩进**：Tab 宽度 4，自动缩进

### 2. 多标签管理 (`tab_manager.py`)
- `QTabWidget` + 可关闭标签按钮
- 每个标签包含一个 `Editor` 实例
- 标签切换时更新窗口标题和状态栏
- `Ctrl+T` 新建，`Ctrl+W` 关闭

### 3. Markdown 预览 (`md_preview.py`)
- `QSplitter` 水平分栏：左侧编辑，右侧预览
- `markdown` 库将 MD 文本转 HTML
- `QTextBrowser` 渲染 HTML，配简易 CSS 样式
- `QTimer` 300ms 防抖后更新预览
- `Ctrl+P` 切换预览显示/隐藏
- 只在 .md 文件时激活，.txt 时隐藏

### 4. 自动保存 (`autosave.py`) — Obsidian 方案
- **有路径的文件**：文本修改后，30 秒防抖 → **直接写入原文件**（无 tmp）
- **新建未命名文件**：30 秒无操作 → 自动保存到 `文档\Notes\`（`%USERPROFILE%\Documents\Notes\`），文件名取首行文字或 `未命名_时间戳.md`
- **默认目录**：首次启动自动创建 `Documents\Notes\`，可在设置中修改
- **关闭标签/窗口时**：立即保存一次
- **手动保存 `Ctrl+S`**：立即写入，已命名文件写原路径，未命名文件写默认目录
- 无临时文件、无备份目录，策略极简，与 Obsidian 一致

### 5. 文件操作 (`file_handler.py`)
- 打开 `.md`, `.txt`, `.markdown` 等纯文本文件
- 自动检测 UTF-8 / GBK 编码
- 拖拽文件到窗口即可打开
- 最近文件列表（存储到 `QSettings`）

### 6. 查找替换 (`find_replace.py`)
- `Ctrl+F` 打开底部查找栏
- 支持高亮匹配、替换、全部替换、大小写敏感

### 7. 设置 (`settings.py`)
- 字体设置：`QFontDialog` 选择字体和大小，存储到 `QSettings`
- 主题切换：浅色/深色模式
- 自动保存间隔

## 开发步骤

### 第 1 步：环境搭建
```bash
cd D:\AIAGENT应用\replace_txt\notepad
python -m venv .venv
.venv\Scripts\activate
pip install PyQt6 PyQt6-QScintilla markdown
```

### 第 2 步：最小可用原型
- `main.py` + `editor.py`：单窗口编辑器，行号 + 语法高亮
- 能打开/保存文件，`Ctrl+B` 加粗

### 第 3 步：标签 + 自动保存
- `tab_manager.py` + `autosave.py` + `file_handler.py`

### 第 4 步：Markdown 预览
- `md_preview.py`：分栏预览 + 防抖更新

### 第 5 步：查找替换 + 设置
- `find_replace.py` + `settings.py`

### 第 6 步：打磨
- 快捷键完善、深色主题、托盘图标、打包 exe

## 文件清单（需创建）

| 文件 | 用途 |
|------|------|
| `main.py` | 启动入口，创建 QApplication |
| `src/app.py` | 主窗口，组装所有模块 |
| `src/editor.py` | QScintilla 编辑器核心 |
| `src/tab_manager.py` | 多标签容器 |
| `src/md_preview.py` | MD 分栏预览 |
| `src/autosave.py` | 定时自动保存 |
| `src/file_handler.py` | 文件 IO + 编码检测 |
| `src/find_replace.py` | 查找替换 UI |
| `src/settings.py` | 配置持久化 |
| `requirements.txt` | 依赖声明（`pip freeze > requirements.txt` 生成） |
| `.gitignore` | 忽略 `.venv/` `__pycache__/` 等 |
| `resources/` | 图标目录 |

## 验证方式

1. 启动 `python main.py`，窗口秒开
2. 输入文字，`Ctrl+B` 加粗可见 `**text**`
3. 等待 30 秒无操作 → 文件自动保存到原路径
4. `Ctrl+S` 手动保存 → 立即写入原文件
5. 打开 `.md` 文件 → 分栏预览可见渲染效果
6. `Ctrl+滚轮` → 字号缩放流畅
7. `Ctrl+F` → 查找功能正常
8. 关闭提示未保存，`Ctrl+Shift+T` 恢复最近关闭标签
