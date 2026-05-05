from PyQt6.Qsci import QsciScintilla
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

from src.markdown_lexer import MarkdownLexer


class Editor(QsciScintilla):
    """QScintilla editor with line numbers, MD syntax highlighting, bold, zoom."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_margins()
        self._setup_caret()
        self._setup_auto_indent()
        self._setup_lexer()
        self._setup_wrap()
        self._setup_highlight()

    def _setup_margins(self):
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, 40)
        self.setMarginsForegroundColor(QColor(128, 128, 128))
        self.setMarginsBackgroundColor(QColor(240, 240, 240))
        self.setMarginLineNumbers(0, True)
        self.setMarginWidth(1, 0)

    def _setup_caret(self):
        self.setCaretWidth(2)
        self.setCaretForegroundColor(QColor(0, 0, 0))
        self.setExtraAscent(0)
        self.setExtraDescent(0)
        font_metrics = self.fontMetrics()
        self.SendScintilla(2699, font_metrics.height())  # SCI_SETLINESPACING

    def _setup_auto_indent(self):
        self.setAutoIndent(True)
        self.setTabWidth(4)
        self.setIndentationGuides(False)
        self.SendScintilla(QsciScintilla.SCI_SETVIEWWS, 0)

    def _setup_lexer(self):
        self._lexer = MarkdownLexer(self)
        self.setLexer(self._lexer)
        from src.settings import Settings
        size = Settings().font_size
        font = QFont("Consolas", size)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(font)

    def _setup_wrap(self):
        self.setWrapMode(QsciScintilla.WrapMode.WrapWord)
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)

    def toggle_bold(self):
        if not self.hasSelectedText():
            return
        line_from, index_from, line_to, index_to = self.getSelection()
        selected = self.selectedText()
        if selected.startswith("**") and selected.endswith("**"):
            new_text = selected[2:-2]
        else:
            new_text = f"**{selected}**"
        start_pos = self.positionFromLineIndex(line_from, index_from)
        self.replaceSelectedText(new_text)
        new_end_pos = start_pos + len(new_text)
        end_line, end_index = self.lineIndexFromPosition(new_end_pos)
        self.setSelection(line_from, index_from, end_line, end_index)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoomIn()
            else:
                self.zoomOut()
            event.accept()
            return
        super().wheelEvent(event)

    # --- Image drag & drop ---

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile() and self._is_image_file(url.toLocalFile()):
                    event.acceptProposedAction()
                    return
        super().dragEnterEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    path = url.toLocalFile()
                    if self._is_image_file(path):
                        self._insert_image_markdown(path)
                        event.acceptProposedAction()
                        return
        super().dropEvent(event)

    @staticmethod
    def _is_image_file(path: str) -> bool:
        import os
        ext = os.path.splitext(path)[1].lower()
        return ext in ('.png', '.jpg', '.jpeg', '.gif', '.bmp',
                       '.svg', '.webp', '.ico', '.tiff')

    def _insert_image_markdown(self, path: str):
        line, col = self.getCursorPosition()
        md_text = f"![]({path})"
        self.insertAt(md_text, line, col)
        self.setCursorPosition(line, col + len(md_text))

    # --- ==highlight== indicator ---

    def _setup_highlight(self):
        self._HL_INDIC = 8
        self.indicatorDefine(
            QsciScintilla.IndicatorStyle.RoundBoxIndicator,
            self._HL_INDIC
        )
        self.setIndicatorForegroundColor(QColor(60, 179, 113, 160), self._HL_INDIC)
        self.setIndicatorOutlineColor(QColor(60, 179, 113, 180), self._HL_INDIC)

        self._highlight_timer = QTimer(self)
        self._highlight_timer.setSingleShot(True)
        self._highlight_timer.timeout.connect(self._apply_highlights)
        self.textChanged.connect(lambda: self._highlight_timer.start(300))

    def _apply_highlights(self):
        import re
        text = self.text()
        self.clearIndicatorRange(0, 0, self.lines() - 1,
                                 self.lineLength(self.lines() - 1), self._HL_INDIC)
        for match in re.finditer(r'==(.+?)==', text):
            start = match.start()
            end = match.end()
            start_line, start_col = self.lineIndexFromPosition(start)
            end_line, end_col = self.lineIndexFromPosition(end)
            self.fillIndicatorRange(
                start_line, start_col,
                end_line, end_col,
                self._HL_INDIC
            )
