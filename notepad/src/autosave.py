import os
import re
from PyQt6.QtCore import QTimer


DEFAULT_DIR = os.path.join(os.path.expanduser("~"), "Documents", "Notes")


class AutoSave:
    """Debounced auto-save (Obsidian-style). Saves directly to original file."""

    def __init__(self, get_content, get_path, set_path, status_callback,
                 tab_manager, interval_ms=30000):
        self.get_content = get_content
        self.get_path = get_path
        self.set_path = set_path
        self.status_callback = status_callback
        self._tab_manager = tab_manager
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._do_save)
        self._interval_ms = interval_ms

    def mark_dirty(self):
        """Mark current editor as dirty and (re)start the timer."""
        editor = self._tab_manager.current_editor()
        if editor:
            self._tab_manager.mark_dirty(id(editor))
        self._timer.start(self._interval_ms)

    def save_now(self):
        """Immediate save (Ctrl+S). Skips timer, only if path exists."""
        self._timer.stop()
        content = self.get_content()
        path = self.get_path()
        if not path:
            return
        self._write(content, path)
        editor = self._tab_manager.current_editor()
        if editor:
            self._tab_manager.mark_clean(id(editor))
            self._tab_manager._update_tab_title(editor)

    def save_to_path(self, content, path):
        """Save to a specific path and mark clean."""
        self._write(content, path)
        editor = self._tab_manager.current_editor()
        if editor:
            self._tab_manager.mark_clean(id(editor))
            self._tab_manager._update_tab_title(editor)

    def _do_save(self):
        """Timer-triggered auto-save. Saves unnamed files to default dir."""
        content = self.get_content()
        path = self.get_path()
        if not path:
            os.makedirs(DEFAULT_DIR, exist_ok=True)
            editor = self._tab_manager.current_editor()
            name = self._tab_manager.filename_candidate(editor) if editor else "未命名"
            safe_name = self._sanitize_filename(name)
            path = os.path.join(DEFAULT_DIR, f"{safe_name}.md")
            self.set_path(path)
        self._write(content, path)
        editor = self._tab_manager.current_editor()
        if editor:
            self._tab_manager.mark_clean(id(editor))
            self._tab_manager._update_tab_title(editor)

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        name = name[:40]
        # Delete all OS-illegal and Markdown formatting characters
        safe = re.sub(r'[<>:"/\\|?*#~`\[\]()]', '', name)
        safe = safe.strip()
        return safe or "未命名"

    def _write(self, content, path):
        try:
            with open(path, "w", encoding="utf-8", newline='') as f:
                f.write(content)
            self.status_callback(f"已保存 {os.path.basename(path)}")
        except OSError as e:
            self.status_callback(f"保存失败: {e}")
