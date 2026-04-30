from PyQt6.Qsci import QsciLexerMarkdown
from PyQt6.QtGui import QFont, QColor


class MarkdownLexer(QsciLexerMarkdown):
    """MD lexer for LiteNotepad.

    Note: PyQt6 QScintilla bindings don't support per-character styling
    (SCI_GETSTYLEAT always returns 0 for all lexers including QsciLexerCPP).
    This lexer defines style properties for reference but visual rendering
    is not guaranteed in this PyQt6 build.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_styles()

    def _setup_styles(self):
        base_font = QFont("Consolas", 11)
        base_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setDefaultFont(base_font)
        self.setDefaultColor(QColor(30, 30, 30))
        self.setDefaultPaper(QColor(255, 255, 255))

        # H1 (style 6 = Level 1 header in QsciLexerMarkdown)
        h1_font = QFont("Consolas", 22)
        h1_font.setBold(True)
        h1_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(h1_font, 6)
        self.setColor(QColor(0, 0, 0), 6)

        # H2 (style 7 = Level 2 header)
        h2_font = QFont("Consolas", 18)
        h2_font.setBold(True)
        h2_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(h2_font, 7)
        self.setColor(QColor(0, 0, 0), 7)

        # H3-H6 (styles 8-11)
        h3_font = QFont("Consolas", 15)
        h3_font.setBold(True)
        h3_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(h3_font, 8)
        self.setColor(QColor(30, 30, 30), 8)

        h4_font = QFont("Consolas", 13)
        h4_font.setBold(True)
        h4_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(h4_font, 9)

        h5_font = QFont("Consolas", 11)
        h5_font.setBold(True)
        h5_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(h5_font, 10)

        h6_font = QFont("Consolas", 11)
        h6_font.setBold(True)
        h6_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(h6_font, 11)

        # Code block (style 12 = Pre-char)
        code_font = QFont("Consolas", 11)
        code_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(code_font, 12)
        self.setPaper(QColor(245, 245, 245), 12)
        self.setColor(QColor(50, 50, 50), 12)

        # Blockquote (style 13)
        bq_font = QFont("Consolas", 11)
        bq_font.setItalic(True)
        bq_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(bq_font, 13)
        self.setColor(QColor(100, 100, 100), 13)

        # Link (style 14)
        link_font = QFont("Consolas", 11)
        link_font.setUnderline(True)
        link_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(link_font, 14)
        self.setColor(QColor(0, 100, 200), 14)

        # === Inline styles (handled by C++ lexer, may or may not render in PyQt6) ===

        # Bold: **text** (style 2) and __text__ (style 3)
        bold_font = QFont("Consolas", 11)
        bold_font.setBold(True)
        bold_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(bold_font, 2)
        self.setFont(bold_font, 3)

        # Italic: *text* (style 4) and _text_ (style 5)
        italic_font = QFont("Consolas", 11)
        italic_font.setItalic(True)
        italic_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(italic_font, 4)
        self.setFont(italic_font, 5)

        # Inline code: `text` (style 19)
        code_inline_font = QFont("Consolas", 11)
        code_inline_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(code_inline_font, 19)
        self.setPaper(QColor(240, 240, 240), 19)
        self.setColor(QColor(200, 50, 50), 19)
