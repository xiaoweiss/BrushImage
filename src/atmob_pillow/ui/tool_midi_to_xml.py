from __future__ import annotations

from PySide6.QtWidgets import QLabel, QGridLayout, QSpinBox, QWidget


class MidiToXmlToolWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)

        layout.addWidget(QLabel("将输入文件夹中的 .mid/.midi 批量转换为 MusicXML (.xml)。"), 0, 0, 1, 2)

        lbl_conc = QLabel("并发数")
        self.sp_concurrency = QSpinBox()
        self.sp_concurrency.setRange(1, 32)
        self.sp_concurrency.setValue(1)

        layout.addWidget(lbl_conc, 1, 0)
        layout.addWidget(self.sp_concurrency, 1, 1)

    def get_params(self) -> dict:
        return {
            "concurrency": int(self.sp_concurrency.value()),
        }
