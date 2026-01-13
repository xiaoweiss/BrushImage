from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QLabel,
    QSpinBox,
    QWidget,
)


class MidiToXmlToolWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)

        layout.addWidget(QLabel("将输入文件夹中的 .mid/.midi 批量转换为 MusicXML (.musicxml)。"), 0, 0, 1, 2)

        lbl_conc = QLabel("并发数")
        self.sp_concurrency = QSpinBox()
        self.sp_concurrency.setRange(1, 32)
        self.sp_concurrency.setValue(1)

        lbl_quant = QLabel("量化")
        self.cb_quantize_mode = QComboBox()
        self.cb_quantize_mode.addItems(["不量化", "自动量化", "八分音符", "十六分音符", "三十二分音符"])
        self.cb_quantize_mode.setCurrentText("自动量化")

        self.cb_remove_tiny_rests = QCheckBox("去除小休止符")

        layout.addWidget(lbl_conc, 1, 0)
        layout.addWidget(self.sp_concurrency, 1, 1)
        layout.addWidget(lbl_quant, 2, 0)
        layout.addWidget(self.cb_quantize_mode, 2, 1)
        layout.addWidget(self.cb_remove_tiny_rests, 3, 0, 1, 2)

    def get_params(self) -> dict:
        mode_text = self.cb_quantize_mode.currentText().strip()
        if mode_text == "自动量化":
            quantize_mode = "auto"
        elif mode_text == "八分音符":
            quantize_mode = "1/8"
        elif mode_text == "十六分音符":
            quantize_mode = "1/16"
        elif mode_text == "三十二分音符":
            quantize_mode = "1/32"
        else:
            quantize_mode = "off"

        return {
            "concurrency": int(self.sp_concurrency.value()),
            "quantize_mode": quantize_mode,
            "remove_tiny_rests": bool(self.cb_remove_tiny_rests.isChecked()),
        }
