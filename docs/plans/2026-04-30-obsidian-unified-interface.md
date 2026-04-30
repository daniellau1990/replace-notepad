# Obsidian 风格统一界面实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将 LiteNotepad 从分栏布局（编辑器+预览面板）改造为 Obsidian 风格的统一界面——编辑器自身呈现 WYSIWYG 效果，智能状态栏显示行/列和可编辑保存路径。

**Architecture:** 移除 QSplitter + MarkdownPreview，新建自定义 MarkdownLexer 让编辑器内渲染 MD 样式，用永久 QLabel 状态栏替代 showMessage()，Fusion 样式 + 极简 QSS。

**Tech Stack:** Python 3.9, PyQt6, QScintilla

**参考:** https://github.com/obsidianmd/obsidian-releases

---

### Task 1: 自定义 MarkdownLexer

**文件:**
- 创建: `notepad/src/markdown_lexer.py`
- 修改: `notepad/src/editor.py:38-44`（替换 lexer 导入）

**说明:** 继承 QsciLexerMarkdown，覆盖标题样式的字体大小（H1=22pt 粗体，H2=18pt 粗体），代码块灰底，链接蓝色，其他保留原 lexer 行为。

**Step 1: 创建 markdown_lexer.py**

```python
from PyQt6.Qsci import QsciLexerMarkdown
from PyQt6.QtGui import QFont, QColor


class MarkdownLexer(QsciLexerMarkdown):
    """Custom MD lexer with Obsidian-style WYSIWYG appearance."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_styles()

    def _setup_styles(self):
        base_font = QFont("Consolas", 11)
        base_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)

        # Default
        self.setDefaultFont(base_font)
        self.setDefaultColor(QColor(30, 30, 30))
        self.setDefaultPaper(QColor(255, 255, 255))

        # H1 (style 1 = MarkdownH1 in QsciLexerMarkdown)
        h1_font = QFont("Consolas", 22)
        h1_font.setBold(True)
        self.setFont(h1_font, 1)
        self.setColor(QColor(0, 0, 0), 1)

        # H2 (style 2 = MarkdownH2)
        h2_font = QFont("Consolas", 18)
        h2_font.setBold(True)
        self.setFont(h2_font, 2)
        self.setColor(QColor(0, 0, 0), 2)

        # H3 (style 3 = MarkdownH3)
        h3_font = QFont("Consolas", 15)
        h3_font.setBold(True)
        self.setFont(h3_font, 3)
        self.setColor(QColor(30, 30, 30), 3)

        # H4-H6 (styles 4-6)
        h4_font = QFont("Consolas", 13)
        h4_font.setBold(True)
        self.setFont(h4_font, 4)

        # Code block (style 9 = MarkdownCodeBlock)
        code_font = QFont("Consolas", 11)
        self.setFont(code_font, 9)
        self.setPaper(QColor(245, 245, 245), 9)
        self.setColor(QColor(50, 50, 50), 9)

        # Inline code (style 8 = MarkdownCode)
        self.setFont(code_font, 8)
        self.setPaper(QColor(240, 240, 240), 8)
        self.setColor(QColor(200, 50, 50), 8)

        # Links (style 7 = MarkdownLink)
        link_font = QFont("Consolas", 11)
        link_font.setUnderline(True)
        self.setFont(link_font, 7)
        self.setColor(QColor(0, 100, 200), 7)

        # Blockquote
        self.setColor(QColor(100, 100, 100), 5)
        self.setFont(base_font, 5)
```

**Step 2: 修改 editor.py**

在 `_setup_lexer` 中将 `QsciLexerMarkdown` 替换为 `MarkdownLexer`：

```python
from src.markdown_lexer import MarkdownLexer  # 替换 import

def _setup_lexer(self):
    self._lexer = MarkdownLexer(self)  # 替换 QsciLexerMarkdown(self)
    ...
```

**Step 3: 验证**

运行 `python main.py`，确认应用启动正常，H1/H2 显示为大号粗体，代码块有灰底。

---

### Task 2: 移除 QSplitter + MarkdownPreview，统一界面

**文件:**
- 修改: `notepad/src/app.py`（多处）
- 不再导入: `from src.md_preview import MarkdownPreview`
- 不再导入: `from PyQt6.QtWidgets import ... QSplitter`

**说明:**
- 删除 `self._splitter`，直接将 `self._tab_manager` 设为 centralWidget
- 删除 `self._md_preview` 所有引用
- 删除 `_toggle_preview` 方法
- 删除 View 菜单（"Markdown 预览" 动作）
- 删除 `_new_tab`、`_on_tab_changed` 中的 preview 连接

**具体修改：**

```python
# 1. 移除 import
# from src.md_preview import MarkdownPreview
# from PyQt6.QtWidgets import ... QSplitter

# 2. __init__ 中：
# 删除：
# self._md_preview = MarkdownPreview()
# self._splitter = QSplitter(Qt.Orientation.Horizontal)
# self._splitter.addWidget(self._tab_manager)
# self._splitter.addWidget(self._md_preview)
# self._splitter.setSizes([500, 400])
# self.setCentralWidget(self._splitter)

# 改为：
self.setCentralWidget(self._tab_manager)

# 3. _new_tab 中：
# 删除：
# self._md_preview.set_editor(editor)
# 和 textChanged 相关连接

# 4. _on_tab_changed 中：
# 删除 self._md_preview.set_editor(editor)

# 5. 删除 _toggle_preview 方法

# 6. _build_menu 中：
# 删除 View 菜单整个块（view_menu + preview_act）
```

**验证:** 运行后编辑器占满整个窗口，没有预览面板，View 菜单消失。

---

### Task 3: 智能状态栏（左侧行/列，右侧保存路径）

**文件:**
- 修改: `notepad/src/app.py`
- 修改: `notepad/src/tab_manager.py`（添加 `current_path_display` 属性或信号）

**说明:**
- 左侧永久 QLabel: `第 X 行，第 Y 列 | N 行`
- 右侧: ClickablePathWidget（显示保存路径，自动保存文件前缀 "auto-save:"）
- 点击路径 → QLineEdit 编辑 → Enter 保存到新路径

**Step 1: 修改 _update_status 为永久 QLabel**

```python
# 在 __init__ 中添加：
self._line_col_label = QLabel("第 1 行，第 1 列 | 0 行")
self._status.addWidget(self._line_col_label)

# 修改 _update_status：
def _update_status(self):
    editor = self._tab_manager.current_editor()
    if not editor:
        return
    lines = editor.lines()
    pos = editor.getCursorPosition()
    self._line_col_label.setText(f"第 {pos[0]+1} 行，第 {pos[1]+1} 列 | {lines} 行")
    self._update_path_display()
```

**Step 2: 添加 ClickablePathWidget（右侧）**

```python
class ClickablePathWidget(QWidget):
    """显示保存路径，点击可编辑。"""
    save_requested = pyqtSignal(str)  # new path

    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(4, 0, 4, 0)

        self._prefix = QLabel("")
        self._prefix.setStyleSheet("color: #888;")
        self._path = QLabel("")
        self._path.setStyleSheet("color: #0066cc; text-decoration: underline;")
        self._path.setCursor(Qt.CursorShape.PointingHandCursor)

        self._layout.addWidget(self._prefix)
        self._layout.addWidget(self._path)

        self._path.mousePressEvent = self._on_click

    def set_path(self, path: str, is_auto_save: bool = True):
        if path:
            self._prefix.setText("auto-save: " if is_auto_save else "")
            self._path.setText(os.path.basename(path))
            self._path.setToolTip(path)
        else:
            self._prefix.setText("")
            self._path.setText("(未保存)")

    def _on_click(self, event):
        # Show inline edit or dialog
        path = self._path.toolTip()
        if not path:
            return
        # Could show QInputDialog or trigger save dialog
        ...
```

**Step 3: 在 status bar 右侧添加**

```python
self._path_widget = ClickablePathWidget()
self._status.addPermanentWidget(self._path_widget)
```

**验证:** 启动后状态栏左侧显示行/列，右侧显示保存路径；点击路径触发编辑。

---

### Task 4: Fusion 样式 + 苹果式简洁设计

**文件:**
- 修改: `notepad/main.py`（添加 Fusion 样式）
- 修改: `notepad/src/app.py`（添加 QSS 样式表）

**说明:**
- `main.py` 中 `app.setStyle("Fusion")`
- `MainWindow.__init__` 中设置样式表：简洁灰白配色，圆角，扁平

**main.py 修改：**
```python
from PyQt6.QtWidgets import QApplication, QStyleFactory

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ...
```

**app.py 样式表（在 __init__ 中）：**
```python
self.setStyleSheet("""
    QMainWindow { background: #ffffff; }
    QTabWidget::pane { border: none; }
    QTabBar::tab {
        padding: 6px 16px;
        border: none;
        border-bottom: 2px solid transparent;
        color: #555;
    }
    QTabBar::tab:selected {
        color: #000;
        border-bottom: 2px solid #007aff;
    }
    QStatusBar {
        background: #f5f5f5;
        border-top: 1px solid #e0e0e0;
        font-size: 12px;
    }
""")
```

**验证:** 界面风格更扁平、简洁。

---

### Task 5: 更新 Version.md

**文件:**
- 修改: `notepad/Version.md`

添加 v0.3.0 条目：
```markdown
## v0.3.0 (2026-04-30)
- Feature: Obsidian 风格统一界面，移除分栏预览面板
- Feature: 自定义 MarkdownLexer 实现编辑器内 WYSIWYG 样式
- Feature: 智能状态栏（左侧行/列 + 右侧可编辑保存路径）
- Feature: 苹果式简洁设计（Fusion 样式 + 极简 QSS）
- Remove: MarkdownPreview 独立预览面板
- Remove: View 菜单（Ctrl+P 预览切换）
```

---

## 验证方法

1. `python main.py` — 正常启动，无报错
2. 编辑器占满整个窗口，无右侧预览面板
3. 输入 `# H1` → 显示为大号粗体，`## H2` → 中号粗体
4. 状态栏左侧显示 `第 1 行，第 1 列 | N 行`
5. 状态栏右侧显示保存路径（自动保存文件有 "auto-save:" 前缀）
6. 点击路径可编辑
7. F12 打开文件，验证路径显示和编辑
8. 界面风格简洁扁平
