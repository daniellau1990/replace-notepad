from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QSpinBox, QSlider, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class FontSizeDialog(QDialog):
    """Simple font size picker with slider, spinbox, and live preview."""

    def __init__(self, current_size: int = 11, parent=None):
        super().__init__(parent)
        self.setWindowTitle("字体大小")
        self.setFixedSize(360, 220)
        self._result_size = current_size
        self._build_ui(current_size)

    def _build_ui(self, current_size: int):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        top = QHBoxLayout()
        top.addStretch()
        label = QLabel("大小:")
        top.addWidget(label)
        self._spin = QSpinBox()
        self._spin.setRange(8, 72)
        self._spin.setValue(current_size)
        self._spin.valueChanged.connect(self._on_spin_changed)
        top.addWidget(self._spin)
        top.addStretch()
        layout.addLayout(top)

        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(8, 72)
        self._slider.setValue(current_size)
        self._slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self._slider)

        self._preview = QLabel("AaBbCcXxYyZz 字体大小预览")
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_preview(current_size)
        layout.addWidget(self._preview)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _on_spin_changed(self, val):
        self._slider.blockSignals(True)
        self._slider.setValue(val)
        self._slider.blockSignals(False)
        self._update_preview(val)

    def _on_slider_changed(self, val):
        self._spin.blockSignals(True)
        self._spin.setValue(val)
        self._spin.blockSignals(False)
        self._update_preview(val)

    def _update_preview(self, size):
        font = QFont("Consolas", size)
        self._preview.setFont(font)
        self._result_size = size

    @property
    def font_size(self) -> int:
        return self._result_size
