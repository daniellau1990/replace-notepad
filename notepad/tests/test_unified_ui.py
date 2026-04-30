"""Tests for unified interface (Task 2)."""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PyQt6.QtWidgets import QSplitter
from src.tab_manager import TabManager
from src.md_preview import MarkdownPreview


class TestUnifiedInterface:
    """MainWindow should not have splitter or preview."""

    def test_app_imports_without_error(self, qapp):
        """All modules should import cleanly without md_preview errors."""
        # This just tests the import chain works
        from src.app import MainWindow
        assert MainWindow is not None

    def test_mainwindow_has_no_splitter(self, qapp):
        """Central widget should be TabManager, not QSplitter."""
        from src.app import MainWindow
        w = MainWindow()
        cw = w.centralWidget()
        assert cw is not None
        assert not isinstance(cw, QSplitter)
        assert isinstance(cw, TabManager)

    def test_mainwindow_has_no_preview(self, qapp):
        """MainWindow should not have MarkdownPreview attribute."""
        from src.app import MainWindow
        w = MainWindow()
        assert not hasattr(w, '_md_preview')
