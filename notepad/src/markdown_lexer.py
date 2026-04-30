from PyQt6.Qsci import QsciLexerMarkdown
from PyQt6.QtGui import QFont, QColor


class MarkdownLexer(QsciLexerMarkdown):
    """Custom MD lexer with Obsidian-style WYSIWYG appearance.

    - H1: 22pt bold, H2: 18pt bold, H3: 15pt bold, H4: 13pt bold
    - Code blocks: gray background (#f5f5f5)
    - Inline code: gray background, reddish text
    - Links: blue underlined
    - Blockquotes: gray text
    """

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

        # Style indices for QsciLexerMarkdown:
        # 0=Default, 1=H1, 2=H2, 3=H3, 4=H4, 5=H5, 6=H6
        # 7=Link, 8=InlineCode, 9=CodeBlock, 10=BlockQuote

        # H1 (style 1)
        h1_font = QFont("Consolas", 22)
        h1_font.setBold(True)
        h1_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(h1_font, 1)
        self.setColor(QColor(0, 0, 0), 1)

        # H2 (style 2)
        h2_font = QFont("Consolas", 18)
        h2_font.setBold(True)
        h2_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(h2_font, 2)
        self.setColor(QColor(0, 0, 0), 2)

        # H3 (style 3)
        h3_font = QFont("Consolas", 15)
        h3_font.setBold(True)
        h3_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(h3_font, 3)
        self.setColor(QColor(30, 30, 30), 3)

        # H4 (style 4)
        h4_font = QFont("Consolas", 13)
        h4_font.setBold(True)
        h4_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(h4_font, 4)

        # H5-H6 (styles 5-6)
        h5_font = QFont("Consolas", 11)
        h5_font.setBold(True)
        h5_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(h5_font, 5)
        self.setFont(h5_font, 6)

        # Links (style 7)
        link_font = QFont("Consolas", 11)
        link_font.setUnderline(True)
        link_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(link_font, 7)
        self.setColor(QColor(0, 100, 200), 7)

        # Inline code (style 8)
        code_font = QFont("Consolas", 11)
        code_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(code_font, 8)
        self.setPaper(QColor(240, 240, 240), 8)
        self.setColor(QColor(200, 50, 50), 8)

        # Code block (style 9)
        self.setFont(code_font, 9)
        self.setPaper(QColor(245, 245, 245), 9)
        self.setColor(QColor(50, 50, 50), 9)

        # Blockquote (style 10)
        bq_font = QFont("Consolas", 11)
        bq_font.setItalic(True)
        bq_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(bq_font, 10)
        self.setColor(QColor(100, 100, 100), 10)
