"""Tests for MarkdownLexer."""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.markdown_lexer import MarkdownLexer


class TestMarkdownLexer:
    """MarkdownLexer should define styles with correct fonts and colors.

    QsciLexerMarkdown C++ style indices:
    1=Special(**/*/`), 2=Strong(**), 3=Strong(__), 4=Emphasis(*), 5=Emphasis(_)
    6=H1, 7=H2, 8=H3, 9=H4, 10=H5, 11=H6
    12=CodeBlock, 15=BlockQuote, 18=Link, 19=CodeBackticks
    """

    def test_lexer_can_be_instantiated(self, qapp):
        lexer = MarkdownLexer()
        assert lexer is not None

    # --- Heading font sizes ---

    def test_h1_font_is_large_and_bold(self, qapp):
        lexer = MarkdownLexer()
        font = lexer.font(6)
        assert font.pointSize() >= 18
        assert font.bold()

    def test_h2_font_is_medium_and_bold(self, qapp):
        lexer = MarkdownLexer()
        font = lexer.font(7)
        assert font.pointSize() >= 14
        assert font.bold()

    def test_h3_font_is_larger_than_default(self, qapp):
        lexer = MarkdownLexer()
        font = lexer.font(8)
        assert font.pointSize() >= 13
        assert font.bold()

    # --- Code block ---

    def test_code_block_has_gray_background(self, qapp):
        lexer = MarkdownLexer()
        paper = lexer.paper(12)
        assert 200 <= paper.red() <= 255
        assert 200 <= paper.green() <= 255
        assert 200 <= paper.blue() <= 255

    # --- Blockquote ---

    def test_blockquote_is_italic(self, qapp):
        lexer = MarkdownLexer()
        font = lexer.font(15)
        assert font.italic()

    # --- Link ---

    def test_link_is_blue(self, qapp):
        lexer = MarkdownLexer()
        color = lexer.color(18)
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
        font = lexer.font(4)
        assert font.italic()

    # --- Inline code (style 19 = CodeBackticks) ---

    def test_inline_code_has_gray_background(self, qapp):
        lexer = MarkdownLexer()
        paper = lexer.paper(19)
        assert 200 <= paper.red() <= 255
        assert 200 <= paper.green() <= 255
