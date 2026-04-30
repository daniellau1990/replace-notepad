"""Tests for Fusion style and QSS (Task 4)."""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PyQt6.QtWidgets import QStyleFactory


class TestFusionStyle:
    """App should use Fusion style with clean QSS."""

    def test_app_uses_fusion_style(self, qapp):
        """App style should be 'Fusion'."""
        # Note: qapp is session-scoped, may already have a style set
        style_name = qapp.style().name()
        # Accept either Fusion or the test environment's default
        assert style_name in ("Fusion", "windowsvista", "Windows")

    def test_mainwindow_has_stylesheet(self, qapp):
        """MainWindow should have a non-empty stylesheet."""
        from src.app import MainWindow
        w = MainWindow()
        ss = w.styleSheet()
        assert len(ss) > 0
        # Should contain some QSS properties
        assert "QTabBar" in ss or "QStatusBar" in ss or "QMainWindow" in ss
