from PyQt6.Qsci import QsciLexerMarkdown
from PyQt6.QtGui import QFont, QColor


# QsciLexerMarkdown C++ style indices:
# 0=Default, 1=Special(**,__,`,~~~), 2=Strong(**), 3=Strong(__), 4=Emphasis(*), 5=Emphasis(_)
# 6=H1, 7=H2, 8=H3, 9=H4, 10=H5, 11=H6
# 12=PreChar(code block), 13=UnorderedList, 14=OrderedList, 15=BlockQuote
# 16=StrikeOut, 17=HorizontalRule, 18=Link, 19=CodeBackticks


class MarkdownLexer(QsciLexerMarkdown):
    """MD lexer with visible heading sizes and consistent inline style colors."""

    _COLOR_DEFAULT = QColor(30, 30, 30)    # near-black
    _COLOR_WHITE = QColor(255, 255, 255)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_styles()

    def _setup_styles(self):
        base = QFont("Consolas", 11)
        base.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setDefaultFont(base)
        self.setDefaultColor(self._COLOR_DEFAULT)
        self.setDefaultPaper(self._COLOR_WHITE)

        # Style 0: Default
        self.setFont(base, 0)
        self.setColor(self._COLOR_DEFAULT, 0)
        self.setPaper(self._COLOR_WHITE, 0)

        # Style 1: Special (markers like **, *, `, ~~)
        spec_font = QFont("Consolas", 11)
        spec_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(spec_font, 1)
        self.setColor(self._COLOR_DEFAULT, 1)
        self.setPaper(self._COLOR_WHITE, 1)

        # Style 2: Strong emphasis via **
        bold_font = QFont("Consolas", 11)
        bold_font.setBold(True)
        bold_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(bold_font, 2)
        self.setColor(self._COLOR_DEFAULT, 2)
        self.setPaper(self._COLOR_WHITE, 2)

        # Style 3: Strong emphasis via __
        self.setFont(bold_font, 3)
        self.setColor(self._COLOR_DEFAULT, 3)
        self.setPaper(self._COLOR_WHITE, 3)

        # Style 4: Emphasis via *
        italic_font = QFont("Consolas", 11)
        italic_font.setItalic(True)
        italic_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(italic_font, 4)
        self.setColor(self._COLOR_DEFAULT, 4)
        self.setPaper(self._COLOR_WHITE, 4)

        # Style 5: Emphasis via _
        self.setFont(italic_font, 5)
        self.setColor(self._COLOR_DEFAULT, 5)
        self.setPaper(self._COLOR_WHITE, 5)

        # H1 (style 6)
        h1 = QFont("Consolas", 22)
        h1.setBold(True)
        h1.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(h1, 6)
        self.setColor(QColor(0, 0, 0), 6)
        self.setPaper(self._COLOR_WHITE, 6)

        # H2 (style 7)
        h2 = QFont("Consolas", 18)
        h2.setBold(True)
        h2.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(h2, 7)
        self.setColor(QColor(0, 0, 0), 7)
        self.setPaper(self._COLOR_WHITE, 7)

        # H3 (style 8)
        h3 = QFont("Consolas", 15)
        h3.setBold(True)
        h3.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(h3, 8)
        self.setColor(self._COLOR_DEFAULT, 8)
        self.setPaper(self._COLOR_WHITE, 8)

        # H4 (style 9)
        h4 = QFont("Consolas", 13)
        h4.setBold(True)
        h4.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(h4, 9)
        self.setColor(self._COLOR_DEFAULT, 9)
        self.setPaper(self._COLOR_WHITE, 9)

        # H5 (style 10)
        h5 = QFont("Consolas", 11)
        h5.setBold(True)
        h5.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(h5, 10)
        self.setColor(QColor(51, 51, 51), 10)
        self.setPaper(self._COLOR_WHITE, 10)

        # H6 (style 11)
        h6 = QFont("Consolas", 11)
        h6.setBold(True)
        h6.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(h6, 11)
        self.setColor(QColor(51, 51, 51), 11)
        self.setPaper(self._COLOR_WHITE, 11)

        # Style 12: Pre-char (code block)
        code = QFont("Consolas", 11)
        code.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(code, 12)
        self.setColor(QColor(50, 50, 50), 12)
        self.setPaper(QColor(245, 245, 245), 12)

        # Style 13: Unordered list
        ul = QFont("Consolas", 11)
        ul.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(ul, 13)
        self.setColor(self._COLOR_DEFAULT, 13)
        self.setPaper(self._COLOR_WHITE, 13)

        # Style 14: Ordered list
        self.setFont(ul, 14)
        self.setColor(self._COLOR_DEFAULT, 14)
        self.setPaper(self._COLOR_WHITE, 14)

        # Style 15: Block quote
        bq = QFont("Consolas", 11)
        bq.setItalic(True)
        bq.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(bq, 15)
        self.setColor(QColor(100, 100, 100), 15)
        self.setPaper(self._COLOR_WHITE, 15)

        # Style 16: Strike out
        strike = QFont("Consolas", 11)
        strike.setStrikeOut(True)
        strike.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(strike, 16)
        self.setColor(QColor(128, 128, 128), 16)
        self.setPaper(self._COLOR_WHITE, 16)

        # Style 17: Horizontal rule
        self.setFont(base, 17)
        self.setColor(QColor(200, 200, 200), 17)
        self.setPaper(self._COLOR_WHITE, 17)

        # Style 18: Link
        link = QFont("Consolas", 11)
        link.setUnderline(True)
        link.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(link, 18)
        self.setColor(QColor(0, 100, 200), 18)
        self.setPaper(self._COLOR_WHITE, 18)

        # Style 19: Code between backticks
        cb = QFont("Consolas", 11)
        cb.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(cb, 19)
        self.setColor(QColor(200, 50, 50), 19)
        self.setPaper(QColor(240, 240, 240), 19)
