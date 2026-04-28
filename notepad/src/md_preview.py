from PyQt6.QtWidgets import QTextBrowser
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont

import markdown


CSS = """<style>
body {
    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
    font-size: 14px;
    line-height: 1.6;
    padding: 16px;
    color: #1a1a1a;
    background: #fafafa;
}
h1 { font-size: 1.8em; border-bottom: 1px solid #ddd; padding-bottom: 6px; }
h2 { font-size: 1.5em; }
h3 { font-size: 1.3em; }
code { background: #e8e8e8; padding: 2px 6px; border-radius: 3px; font-family: Consolas, monospace; }
pre { background: #f0f0f0; padding: 12px; border-radius: 4px; overflow-x: auto; }
pre code { background: none; padding: 0; }
blockquote { border-left: 4px solid #ddd; margin-left: 0; padding-left: 16px; color: #666; }
table { border-collapse: collapse; }
th, td { border: 1px solid #ccc; padding: 6px 12px; }
</style>"""


class MarkdownPreview(QTextBrowser):
    """Markdown preview panel with 300ms debounce and auto-render."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOpenExternalLinks(True)
        self.setFont(QFont("Segoe UI", 12))
        self._editor = None

        self._debounce = QTimer()
        self._debounce.setSingleShot(True)
        self._debounce.timeout.connect(self._render)

    def set_editor(self, editor):
        self._editor = editor

    def schedule_render(self):
        self._debounce.start(300)

    def _render(self):
        if not self._editor:
            return
        text = self._editor.text()
        html = markdown.markdown(text, extensions=['fenced_code', 'tables', 'codehilite'])
        self.setHtml(CSS + html)
