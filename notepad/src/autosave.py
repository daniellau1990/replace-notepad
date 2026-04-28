import os
from PyQt6.QtCore import QTimer


DEFAULT_DIR = os.path.join(os.path.expanduser("~"), "Documents", "Notes")


class AutoSave:
    """Debounced auto-save (Obsidian-style). Saves directly to original file."""

    def __init__(self, get_content, get_path, set_path, status_callback,
                 interval_ms=30000):
        """
        get_content: callable → str (editor content)
        get_path:    callable → str or None (current file path)
        set_path:    callable(str) → None (set current file path)
        status_callback: callable(str) → None (show status message)
        """
        self.get_content = get_content
        self.get_path = get_path
        self.set_path = set_path
        self.status_callback = status_callback
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._do_save)
        self._interval_ms = interval_ms
        self._dirty = False

    def mark_dirty(self):
        """Call on every text change."""
        self._dirty = True
        self._timer.start(self._interval_ms)

    def save_now(self):
        """Immediate save (Ctrl+S / close)."""
        self._timer.stop()
        self._do_save()

    def _do_save(self):
        if not self._dirty:
            return
        content = self.get_content()
        path = self.get_path()
        if not path:
            # Unnamed file — auto-save to default directory
            os.makedirs(DEFAULT_DIR, exist_ok=True)
            first_line = content.split("\n", 1)[0].strip()
            name = first_line if first_line else "未命名"
            # Truncate long filenames
            name = name[:40]
            safe_name = "".join(c if c.isalnum() or c in " _-." else "_" for c in name)
            safe_name = safe_name or "未命名"
            path = os.path.join(DEFAULT_DIR, f"{safe_name}.md")
            self.set_path(path)

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self._dirty = False
            self.status_callback(f"已保存 {os.path.basename(path)}")
        except OSError as e:
            self.status_callback(f"保存失败: {e}")
