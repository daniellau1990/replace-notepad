"""Tests for smart status bar (Task 3)."""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PyQt6.QtWidgets import QLabel, QStatusBar
from PyQt6.QtCore import Qt


class TestSmartStatusBar:
    """MainWindow status bar should have permanent labels for line/col and path."""

    def test_status_bar_has_line_col_label(self, qapp):
        """Status bar left side should have a QLabel showing line/col."""
        from src.app import MainWindow
        w = MainWindow()
        sb = w.statusBar()
        # Find QLabel in status bar widgets
        labels = [c for c in sb.findChildren(QLabel) if "行" in c.text()]
        assert len(labels) >= 1, "No line/col label found"
        assert "行" in labels[0].text()

    def test_status_bar_has_path_widget(self, qapp):
        """Status bar right side should have a ClickablePathWidget."""
        from src.app import MainWindow
        w = MainWindow()
        sb = w.statusBar()
        from src.app import ClickablePathWidget
        path_widgets = sb.findChildren(ClickablePathWidget)
        assert len(path_widgets) >= 1

    def test_path_widget_shows_unsaved_for_new_tab(self, qapp):
        """New unnamed tab should show (未保存)."""
        from src.app import ClickablePathWidget
        pw = ClickablePathWidget()
        pw.set_path("", is_auto_save=False)
        assert "未保存" in pw._path.text()

    def test_path_widget_shows_basename_for_saved(self, qapp):
        """Saved file should show basename with optional prefix."""
        from src.app import ClickablePathWidget
        pw = ClickablePathWidget()
        pw.set_path("/tmp/test.md", is_auto_save=True)
        assert "test.md" in pw._path.text()
        assert "auto-save" in pw._prefix.text()

    def test_path_widget_clickable(self, qapp):
        """Path label should have pointing hand cursor."""
        from src.app import ClickablePathWidget
        pw = ClickablePathWidget()
        pw.set_path("/tmp/test.md", is_auto_save=False)
        assert pw._path.cursor().shape() == Qt.CursorShape.PointingHandCursor
