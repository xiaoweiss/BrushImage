from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QWidget,
)


OUTPUT_FORMATS = ["JPG", "PNG", "WEBP"]


class ImageConvertToolWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)

        # 输入过滤
        lbl_filter = QLabel("仅转换后缀")
        self.cb_input_filter = QComboBox()
        self.cb_input_filter.addItems(["全部图片", "仅 PNG", "仅 JPG/JPEG", "自定义..."])
        self.ed_custom_filter = QLineEdit()
        self.ed_custom_filter.setPlaceholderText("例如: png,jpg,webp")
        self.ed_custom_filter.setVisible(False)
        self.cb_input_filter.currentTextChanged.connect(self._on_filter_changed)

        # 输出格式
        lbl_format = QLabel("输出格式")
        self.cb_format = QComboBox()
        self.cb_format.addItems(OUTPUT_FORMATS)
        self.cb_format.setCurrentText("JPG")

        # 质量/压缩率
        lbl_q = QLabel("质量/压缩率")
        self.sp_quality = QSpinBox()
        self.sp_quality.setRange(1, 100)
        self.sp_quality.setValue(90)

        # 并发数
        lbl_conc = QLabel("并发数")
        self.sp_concurrency = QSpinBox()
        self.sp_concurrency.setRange(1, 32)
        self.sp_concurrency.setValue(1)

        layout.addWidget(lbl_filter, 0, 0)
        layout.addWidget(self.cb_input_filter, 0, 1)
        layout.addWidget(QLabel(""), 1, 0)
        layout.addWidget(self.ed_custom_filter, 1, 1)

        layout.addWidget(lbl_format, 2, 0)
        layout.addWidget(self.cb_format, 2, 1)
        layout.addWidget(lbl_q, 3, 0)
        layout.addWidget(self.sp_quality, 3, 1)
        layout.addWidget(lbl_conc, 4, 0)
        layout.addWidget(self.sp_concurrency, 4, 1)

    def _on_filter_changed(self, text: str) -> None:
        self.ed_custom_filter.setVisible(text == "自定义...")

    def get_params(self) -> dict:
        filter_text = self.cb_input_filter.currentText().strip()
        if filter_text == "仅 PNG":
            mode = "only_png"
        elif filter_text == "仅 JPG/JPEG":
            mode = "only_jpg"
        elif filter_text == "自定义...":
            mode = "custom"
        else:
            mode = "all"

        out_fmt = self.cb_format.currentText().strip().lower()
        return {
            "input_filter_mode": mode,
            "input_filter_custom": self.ed_custom_filter.text().strip(),
            "output_format": out_fmt,
            "quality": int(self.sp_quality.value()),
            "concurrency": int(self.sp_concurrency.value()),
        }
