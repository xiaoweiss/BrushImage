from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QLabel, QSpinBox, QWidget


class ImageResizeToolWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)

        lbl_w = QLabel("目标宽度")
        self.sp_width = QSpinBox()
        self.sp_width.setRange(0, 20000)
        self.sp_width.setValue(0)

        lbl_h = QLabel("目标高度")
        self.sp_height = QSpinBox()
        self.sp_height.setRange(0, 20000)
        self.sp_height.setValue(0)

        lbl_q = QLabel("质量/压缩 (1-100)")
        self.sp_quality = QSpinBox()
        self.sp_quality.setRange(1, 100)
        self.sp_quality.setValue(100)

        layout.addWidget(lbl_w, 0, 0)
        layout.addWidget(self.sp_width, 0, 1)
        layout.addWidget(lbl_h, 1, 0)
        layout.addWidget(self.sp_height, 1, 1)
        layout.addWidget(lbl_q, 2, 0)
        layout.addWidget(self.sp_quality, 2, 1)

    def get_params(self) -> dict:
        return {
            "target_w": int(self.sp_width.value()),
            "target_h": int(self.sp_height.value()),
            "quality": int(self.sp_quality.value()),
        }
