from PyQt6.Qsci import QsciScintilla, QsciLexerMarkdown
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor


class Editor(QsciScintilla):
    """QScintilla editor with line numbers, MD syntax highlighting, bold, zoom."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_margins()
        self._setup_caret()
        self._setup_auto_indent()
        self._setup_lexer()

    def _setup_margins(self):
        # Line number margin
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, 40)
        self.setMarginsForegroundColor(QColor(128, 128, 128))
        self.setMarginsBackgroundColor(QColor(240, 240, 240))
        self.setMarginLineNumbers(0, True)

        # Symbol margin (for fold markers etc.) — hide it
        self.setMarginWidth(1, 0)

    def _setup_caret(self):
        self.setCaretWidth(2)
        self.setCaretForegroundColor(QColor(0, 0, 0))

    def _setup_auto_indent(self):
        self.setAutoIndent(True)
        self.setTabWidth(4)
        self.setIndentationGuides(True)
        self.setIndentationGuidesForegroundColor(QColor(200, 200, 200))
        self.setIndentationGuidesBackgroundColor(QColor(240, 240, 240))

    def _setup_lexer(self):
        self._lexer = QsciLexerMarkdown(self)
        font = QFont("Consolas", 11)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self._lexer.setDefaultFont(font)
        self.setLexer(self._lexer)
        self.setFont(font)

    def toggle_bold(self):
        """Wrap selected text with **, or remove them if already wrapped."""
        if not self.hasSelectedText():
            return
        line_from, index_from, line_to, index_to = self.getSelection()
        selected = self.selectedText()
        if selected.startswith("**") and selected.endswith("**"):
            new_text = selected[2:-2]
        else:
            new_text = f"**{selected}**"
        start_pos = self.positionFromLineIndex(line_from, index_from)
        self.replaceSelectedText(new_text)
        new_end_pos = start_pos + len(new_text)
        end_line, end_index = self.lineIndexFromPosition(new_end_pos)
        self.setSelection(line_from, index_from, end_line, end_index)

    def wheelEvent(self, event):
        """Ctrl+Scroll to zoom in/out."""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoomIn()
            else:
                self.zoomOut()
            event.accept()
            return
        super().wheelEvent(event)
