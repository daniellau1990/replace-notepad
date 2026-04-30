"""Pytest fixtures for LiteNotepad tests."""
import sys
import os
import pytest
from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication once per test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
