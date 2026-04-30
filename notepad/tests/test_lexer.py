"""Tests for MarkdownLexer."""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.markdown_lexer import MarkdownLexer


class TestMarkdownLexer:
    """MarkdownLexer should define heading/code/quote styles correctly.

    Note: PyQt6 QScintilla bindings don't support per-character style
    read-back (SCI_GETSTYLEAT always returns 0 for all lexers).
    These tests verify the lexer's style DEFINITIONS are correct,
    not that they render visually.
    """

    def test_lexer_can_be_instantiated(self, qapp):
        """Lexer should create without error."""
        lexer = MarkdownLexer()
        assert lexer is not None

    def test_h1_font_is_large_and_bold(self, qapp):
        """H1 (style 6) should be >=18pt and bold."""
        lexer = MarkdownLexer()
        font = lexer.font(6)
        assert font.pointSize() >= 18
        assert font.bold()

    def test_h2_font_is_medium_and_bold(self, qapp):
        """H2 (style 7) should be >=14pt and bold."""
        lexer = MarkdownLexer()
        font = lexer.font(7)
        assert font.pointSize() >= 14
        assert font.bold()

    def test_h3_font_is_larger_than_default(self, qapp):
        """H3 (style 8) should be >11pt."""
        lexer = MarkdownLexer()
        font = lexer.font(8)
        assert font.pointSize() >= 13
        assert font.bold()

    def test_code_block_has_gray_background(self, qapp):
        """Code block (style 12) should have gray-ish background."""
        lexer = MarkdownLexer()
        paper = lexer.paper(12)
        assert 200 <= paper.red() <= 255
        assert 200 <= paper.green() <= 255
        assert 200 <= paper.blue() <= 255

    def test_blockquote_is_italic(self, qapp):
        """Blockquote (style 13) should be italic."""
        lexer = MarkdownLexer()
        font = lexer.font(13)
        assert font.italic()

    def test_link_is_blue(self, qapp):
        """Link (style 14) should have blue color."""
        lexer = MarkdownLexer()
        color = lexer.color(14)
        assert color.blue() > 150
        assert color.red() < 100

    def test_default_font_is_consolas(self, qapp):
        """Default font should be Consolas at 11pt."""
        lexer = MarkdownLexer()
        font = lexer.defaultFont(0)
        assert "Consolas" in font.family()
        assert font.pointSize() == 11
