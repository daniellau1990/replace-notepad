from PyQt6.QtCore import QSettings


class Settings:
    """Persistent settings using QSettings."""

    def __init__(self):
        self._settings = QSettings("LiteNotepad", "Settings")

    @property
    def font_size(self) -> int:
        return int(self._settings.value("fontSize", 11))

    @font_size.setter
    def font_size(self, value: int) -> None:
        self._settings.setValue("fontSize", value)

    @property
    def auto_save_interval(self) -> int:
        return int(self._settings.value("autoSaveInterval", 30000))

    @auto_save_interval.setter
    def auto_save_interval(self, value: int) -> None:
        self._settings.setValue("autoSaveInterval", value)

    @property
    def theme(self) -> str:
        return self._settings.value("theme", "light")

    @theme.setter
    def theme(self, value: str) -> None:
        self._settings.setValue("theme", value)

    @property
    def window_geometry(self) -> bytes:
        return self._settings.value("windowGeometry", b"")

    @window_geometry.setter
    def window_geometry(self, value: bytes) -> None:
        self._settings.setValue("windowGeometry", value)

    @property
    def default_dir(self) -> str:
        import os
        return self._settings.value("defaultDir", os.path.join(os.path.expanduser("~"), "Documents", "Notes"))

    @default_dir.setter
    def default_dir(self, value: str) -> None:
        self._settings.setValue("defaultDir", value)
