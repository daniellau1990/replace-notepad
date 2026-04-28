from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, \
    QPushButton, QCheckBox, QLabel
from PyQt6.QtCore import Qt, pyqtSignal


class FindReplace(QWidget):
    """Find/replace bar at the bottom of the editor."""

    find_next_requested = pyqtSignal(str, bool)
    replace_requested = pyqtSignal(str, str, bool)
    replace_all_requested = pyqtSignal(str, str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        # Find row
        find_row = QHBoxLayout()
        self._find_input = QLineEdit()
        self._find_input.setPlaceholderText("查找...")
        self._find_input.setFixedWidth(250)
        self._find_btn = QPushButton("查找下一个")
        self._find_btn.clicked.connect(self._on_find_next)
        self._find_input.returnPressed.connect(self._on_find_next)

        self._case_cb = QCheckBox("大小写敏感")
        self._find_prev_btn = QPushButton("上一个")

        find_row.addWidget(QLabel("查找:"))
        find_row.addWidget(self._find_input)
        find_row.addWidget(self._find_btn)
        find_row.addWidget(self._find_prev_btn)
        find_row.addWidget(self._case_cb)
        find_row.addStretch()
        layout.addLayout(find_row)

        # Replace row
        replace_row = QHBoxLayout()
        self._replace_input = QLineEdit()
        self._replace_input.setPlaceholderText("替换为...")
        self._replace_input.setFixedWidth(250)
        self._replace_btn = QPushButton("替换")
        self._replace_btn.clicked.connect(self._on_replace)
        self._replace_all_btn = QPushButton("全部替换")
        self._replace_all_btn.clicked.connect(self._on_replace_all)

        replace_row.addWidget(QLabel("替换:"))
        replace_row.addWidget(self._replace_input)
        replace_row.addWidget(self._replace_btn)
        replace_row.addWidget(self._replace_all_btn)
        replace_row.addStretch()
        layout.addLayout(replace_row)

    def _on_find_next(self):
        text = self._find_input.text()
        if text:
            self.find_next_requested.emit(text, self._case_cb.isChecked())

    def _on_replace(self):
        find = self._find_input.text()
        replace = self._replace_input.text()
        if find:
            self.replace_requested.emit(find, replace, self._case_cb.isChecked())

    def _on_replace_all(self):
        find = self._find_input.text()
        replace = self._replace_input.text()
        if find:
            self.replace_all_requested.emit(find, replace, self._case_cb.isChecked())

    def show(self):
        super().show()
        self._find_input.setFocus()
        self._find_input.selectAll()

    def hide(self):
        super().hide()
        self.parent().setFocus() if self.parent() else None

    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
