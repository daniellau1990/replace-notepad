"""Tests for tab title — shows filename with extension, decoupled from first line."""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestTabTitle:
    """Tab title shows filename with .md extension, not first line content."""

    def test_new_unnamed_tab_shows_md_extension(self, qapp):
        from src.tab_manager import TabManager
        tm = TabManager()
        editor = tm.add_new_tab()
        idx = tm.indexOf(editor)
        title = tm.tabText(idx).replace(" ●", "")
        assert title == "未命名1.md"

    def test_named_file_tab_shows_basename(self, qapp):
        from src.tab_manager import TabManager
        tm = TabManager()
        editor = tm.add_new_tab(content="", path="/tmp/myfile.txt")
        idx = tm.indexOf(editor)
        title = tm.tabText(idx).replace(" ●", "")
        assert title == "myfile.txt"

    def test_tab_title_unchanged_when_first_line_changes(self, qapp):
        from src.tab_manager import TabManager
        tm = TabManager()
        editor = tm.add_new_tab()
        idx = tm.indexOf(editor)
        original = tm.tabText(idx).replace(" ●", "")
        editor.setText("**新标题**\n正文\n")
        tm._update_tab_title(editor)
        new_title = tm.tabText(idx).replace(" ●", "")
        assert new_title == original, f"Tab changed from '{original}' to '{new_title}'"

    def test_filename_candidate_returns_default_name_no_ext(self, qapp):
        from src.tab_manager import TabManager
        tm = TabManager()
        editor = tm.add_new_tab()
        name = tm.filename_candidate(editor)
        assert name == "未命名1"

    def test_filename_candidate_for_saved_file(self, qapp):
        from src.tab_manager import TabManager
        tm = TabManager()
        editor = tm.add_new_tab(content="", path="/tmp/hello.md")
        name = tm.filename_candidate(editor)
        assert name == "hello"

    def test_dirty_marker_appears(self, qapp):
        from src.tab_manager import TabManager
        tm = TabManager()
        editor = tm.add_new_tab()
        tm._on_editor_changed(editor)
        assert "●" in tm.tabText(tm.indexOf(editor))

    def test_dirty_marker_clears(self, qapp):
        from src.tab_manager import TabManager
        tm = TabManager()
        editor = tm.add_new_tab()
        eid = id(editor)
        tm.mark_dirty(eid)
        tm._update_tab_title(editor)
        assert "●" in tm.tabText(tm.indexOf(editor))
        tm.mark_clean(eid)
        tm._update_tab_title(editor)
        assert "●" not in tm.tabText(tm.indexOf(editor))
