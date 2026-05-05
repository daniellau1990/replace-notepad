from PyQt6.Qsci import QsciLexerMarkdown
from PyQt6.QtGui import QFont, QColor


# QsciLexerMarkdown C++ style indices:
# 0=Default, 1=Special, 2=Strong(**), 3=Strong(__), 4=Emphasis(*), 5=Emphasis(_)
# 6=H1, 7=H2, 8=H3, 9=H4, 10=H5, 11=H6
# 12=CodeBlock, 15=BlockQuote, 18=Link, 19=CodeBackticks


class MarkdownLexer(QsciLexerMarkdown):
    """MD lexer with visible heading sizes and inline style colors.

    Note: PyQt6 QScintilla doesn't apply styleText() to editor text, so these
    style definitions serve as fallback for any characters the C++ lexer
    styles. Actual visual highlighting is done via indicators in Editor.
    """

    _COLOR_DEFAULT = QColor(30, 30, 30)
    _COLOR_WHITE = QColor(255, 255, 255)
    _COLOR_BURGUNDY = QColor(178, 34, 34)  # for italic emphasis

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
        self._set_style(1, 11, False, False, (30, 30, 30), (255, 255, 255))

        # Style 2: Strong emphasis via **
        self._set_style(2, 11, True, False, (30, 30, 30), (255, 255, 255))

        # Style 3: Strong emphasis via __
        self._set_style(3, 11, True, False, (30, 30, 30), (255, 255, 255))

        # Style 4: Emphasis via * (burgundy + italic)
        self._set_style(4, 11, False, True, (178, 34, 34), (255, 255, 255))

        # Style 5: Emphasis via _
        self._set_style(5, 11, False, True, (178, 34, 34), (255, 255, 255))

        # H1-H6: heading with distinct sizes and colors
        self._set_style(6, 22, True, False, (0, 0, 0), (255, 255, 255))     # H1
        self._set_style(7, 18, True, False, (0, 0, 0), (255, 255, 255))     # H2
        self._set_style(8, 15, True, False, (30, 30, 30), (255, 255, 255))  # H3
        self._set_style(9, 13, True, False, (30, 30, 30), (255, 255, 255))  # H4
        self._set_style(10, 11, True, False, (51, 51, 51), (255, 255, 255))  # H5
        self._set_style(11, 11, True, False, (51, 51, 51), (255, 255, 255))  # H6

        # Code block
        self._set_style(12, 11, False, False, (50, 50, 50), (245, 245, 245))

        # Unordered list
        self._set_style(13, 11, False, False, (30, 30, 30), (255, 255, 255))

        # Ordered list
        self._set_style(14, 11, False, False, (30, 30, 30), (255, 255, 255))

        # Block quote
        self._set_style(15, 11, False, True, (102, 102, 102), (255, 255, 255))

        # Strike out
        self._set_style(16, 11, False, False, (128, 128, 128), (255, 255, 255),
                        strike=True)

        # Horizontal rule
        self._set_style(17, 11, False, False, (200, 200, 200), (255, 255, 255))

        # Link
        self._set_style(18, 11, False, False, (0, 100, 200), (255, 255, 255),
                        underline=True)

        # Code between backticks
        self._set_style(19, 11, False, False, (200, 50, 50), (240, 240, 240))

    def _set_style(self, index, size, bold, italic, fg, bg, underline=False,
                   strike=False):
        font = QFont("Consolas", size)
        font.setBold(bold)
        font.setItalic(italic)
        font.setStrikeOut(strike)
        font.setUnderline(underline)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(font, index)
        self.setColor(QColor(*fg), index)
        self.setPaper(QColor(*bg), index)

    def update_font_size(self, size: int):
        """Reapply font size to all style definitions (0-19)."""
        for idx in range(20):
            font = self.font(idx)
            font.setPointSize(size)
            self.setFont(font, idx)
