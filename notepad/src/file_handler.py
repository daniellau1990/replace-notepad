import os
from PyQt6.QtCore import QSettings


class FileHandler:
    """File I/O with UTF-8/GBK detection and recent files list."""

    RECENT_MAX = 10

    def __init__(self):
        self._settings = QSettings("LiteNotepad", "FileHandler")

    @staticmethod
    def detect_encoding(path: str) -> str:
        """Try UTF-8 first, fall back to GBK."""
        with open(path, "rb") as f:
            raw = f.read(3)
        # BOM check
        if raw[:3] == b"\xef\xbb\xbf":
            return "utf-8-sig"
        try:
            with open(path, "r", encoding="utf-8") as f:
                f.read()
            return "utf-8"
        except UnicodeDecodeError:
            return "gbk"

    def read_file(self, path: str) -> str:
        encoding = self.detect_encoding(path)
        with open(path, "r", encoding=encoding) as f:
            return f.read()

    def write_file(self, path: str, content: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    # --- Recent files ---

    def recent_files(self) -> list:
        files = self._settings.value("recentFiles", [])
        if isinstance(files, list):
            return [f for f in files if os.path.exists(f)]
        return []

    def add_recent(self, path: str) -> None:
        files = self.recent_files()
        if path in files:
            files.remove(path)
        files.insert(0, path)
        self._settings.setValue("recentFiles", files[:self.RECENT_MAX])

    def clear_recent(self) -> None:
        self._settings.setValue("recentFiles", [])
