"""Tests for MarkdownLexer (Task 1)."""
import sys
import os
import pytest

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PyQt6.QtGui import QFont
from src.markdown_lexer import MarkdownLexer


class TestMarkdownLexer:
    """MarkdownLexer should render headings large and bold, code with gray bg."""

    def test_lexer_can_be_instantiated(self, qapp):
        """Lexer should create without error."""
        lexer = MarkdownLexer()
        assert lexer is not None

    def test_h1_font_is_large_and_bold(self, qapp):
        """H1 (style 1) should be ≥18pt and bold."""
        lexer = MarkdownLexer()
        font = lexer.font(1)
        assert font.pointSize() >= 18
        assert font.bold()

    def test_h2_font_is_medium_and_bold(self, qapp):
        """H2 (style 2) should be ≥14pt and bold."""
        lexer = MarkdownLexer()
        font = lexer.font(2)
        assert font.pointSize() >= 14
        assert font.bold()

    def test_code_block_has_gray_background(self, qapp):
        """Code block (style 9) should have gray-ish background paper."""
        lexer = MarkdownLexer()
        paper = lexer.paper(9)
        # Gray-ish: R, G, B should all be >200 and <255
        assert 200 <= paper.red() <= 255
        assert 200 <= paper.green() <= 255
        assert 200 <= paper.blue() <= 255

    def test_link_is_blue(self, qapp):
        """Link (style 7) should have blue color."""
        lexer = MarkdownLexer()
        color = lexer.color(7)
        # Blue (R low, G low, B high)
        assert color.blue() > 150
        assert color.red() < 100

    def test_default_font_is_consolas(self, qapp):
        """Default font should be Consolas at 11pt."""
        lexer = MarkdownLexer()
        font0 = lexer.font(0)
        assert "Consolas" in font0.family()
        assert font0.pointSize() == 11
