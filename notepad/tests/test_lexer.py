"""Tests for MarkdownLexer style definitions.

NOTE: PyQt6 QScintilla 2.14.1 cannot apply Python-side styles to editor text
(SCI_SETSTYLING, SCI_SETSTYLES, and indicators all silently fail from Python).
These tests verify the style definitions are stored correctly in the lexer.
Full visual highlighting requires the C++ lexer's partial styling.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.markdown_lexer import MarkdownLexer

# QsciLexerMarkdown C++ style indices:
# 0=Default, 1=Special, 2=Strong(**), 3=Strong(__), 4=Emphasis(*), 5=Emphasis(_)
# 6=H1, 7=H2, 8=H3, 9=H4, 10=H5, 11=H6
# 12=CodeBlock, 15=BlockQuote, 18=Link, 19=CodeBackticks


class TestMarkdownLexer:
    """MarkdownLexer should define styles with correct fonts and colors."""

    def test_lexer_can_be_instantiated(self, qapp):
        lexer = MarkdownLexer()
        assert lexer is not None

    # --- Heading font sizes ---

    def test_h1_font_is_large_and_bold(self, qapp):
        lexer = MarkdownLexer()
        font = lexer.font(6)  # H1 = style 6
        assert font.pointSize() >= 18
        assert font.bold()

    def test_h2_font_is_medium_and_bold(self, qapp):
        lexer = MarkdownLexer()
        font = lexer.font(7)  # H2 = style 7
        assert font.pointSize() >= 14
        assert font.bold()

    def test_h3_font_is_larger_than_default(self, qapp):
        lexer = MarkdownLexer()
        font = lexer.font(8)  # H3 = style 8
        assert font.pointSize() >= 13
        assert font.bold()

    # --- Code block ---

    def test_code_block_has_gray_background(self, qapp):
        lexer = MarkdownLexer()
        paper = lexer.paper(12)  # CodeBlock = style 12
        assert 200 <= paper.red() <= 255
        assert 200 <= paper.green() <= 255
        assert 200 <= paper.blue() <= 255

    # --- Blockquote ---

    def test_blockquote_is_italic(self, qapp):
        lexer = MarkdownLexer()
        font = lexer.font(15)  # BlockQuote = style 15
        assert font.italic()

    # --- Link ---

    def test_link_is_blue(self, qapp):
        lexer = MarkdownLexer()
        color = lexer.color(18)  # Link = style 18
        assert color.blue() > 150
        assert color.red() < 100

    # --- Default ---

    def test_default_font_is_consolas(self, qapp):
        lexer = MarkdownLexer()
        font = lexer.font(0)
        assert "Consolas" in font.family()
        assert font.pointSize() == 11

    # --- Inline bold (style 2 = Strong via **) ---

    def test_bold_style_font_is_bold(self, qapp):
        lexer = MarkdownLexer()
        font = lexer.font(2)
        assert font.bold()

    # --- Inline italic (style 4 = Emphasis via *) ---

    def test_italic_style_is_italic(self, qapp):
        lexer = MarkdownLexer()
        font = lexer.font(4)  # Emphasis = style 4
        assert font.italic()

    def test_italic_is_burgundy(self, qapp):
        """Emphasis (*text*) should be burgundy color."""
        lexer = MarkdownLexer()
        color = lexer.color(4)  # Emphasis = style 4
        assert color.red() > 100  # high red
        assert color.green() < 100  # low green
        assert color.blue() < 100  # low blue

    # --- Inline code (style 19 = CodeBackticks) ---

    def test_inline_code_has_gray_background(self, qapp):
        lexer = MarkdownLexer()
        paper = lexer.paper(19)  # CodeBackticks = style 19
        assert 200 <= paper.red() <= 255
        assert 200 <= paper.green() <= 255
