from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .tool_image_convert import ImageConvertToolWidget
from .tool_image_resize import ImageResizeToolWidget


class DropArea(QLabel):
    file_dropped = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(110)
        self.setText("拖拽单张图片到这里")
        self.setStyleSheet(
            "border: 2px dashed #d9d9d9; border-radius: 10px; padding: 18px; background: #fafafa; color: #666;"
        )

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if not urls:
            return
        local = urls[0].toLocalFile()
        if local:
            self.file_dropped.emit(local)


class ImageToolsWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)

        # 模式
        lbl_mode = QLabel("模式")
        self.cb_mode = QComboBox()
        self.cb_mode.addItems(["批量(文件夹)", "单文件(拖拽)"])

        # 功能
        lbl_func = QLabel("功能")
        self.cb_func = QComboBox()
        self.cb_func.addItems(["尺寸调整", "格式转换", "尺寸调整+格式转换"])

        # 子参数页：
        # 0 尺寸调整
        # 1 格式转换
        # 2 组合（同时显示两套参数）
        self.stack = QStackedWidget()

        # 注意：同一个 QWidget 不能同时被 addWidget 到两个父布局中。
        # 所以“组合页”要使用独立实例。
        self.page_resize_single = ImageResizeToolWidget()
        self.page_convert_single = ImageConvertToolWidget()

        self.page_combo = QWidget()
        combo_layout = QVBoxLayout(self.page_combo)
        combo_layout.setContentsMargins(0, 0, 0, 0)
        combo_layout.setSpacing(10)

        self.page_resize_combo = ImageResizeToolWidget()
        self.page_convert_combo = ImageConvertToolWidget()

        gb_resize = QGroupBox("尺寸调整")
        gb_resize_layout = QVBoxLayout(gb_resize)
        gb_resize_layout.setContentsMargins(10, 12, 10, 10)
        gb_resize_layout.addWidget(self.page_resize_combo)

        gb_convert = QGroupBox("格式转换")
        gb_convert_layout = QVBoxLayout(gb_convert)
        gb_convert_layout.setContentsMargins(10, 12, 10, 10)
        gb_convert_layout.addWidget(self.page_convert_combo)

        combo_layout.addWidget(gb_resize)
        combo_layout.addWidget(gb_convert)

        self.stack.addWidget(self.page_resize_single)
        self.stack.addWidget(self.page_convert_single)
        self.stack.addWidget(self.page_combo)

        # 单文件区域
        self.gb_single = QGroupBox("单文件")
        single_layout = QVBoxLayout(self.gb_single)
        single_layout.setContentsMargins(10, 12, 10, 10)
        single_layout.setSpacing(10)

        self.drop = DropArea()
        self.drop.file_dropped.connect(self._on_file_dropped)

        row_in = QHBoxLayout()
        self.ed_single_in = QLineEdit()
        self.ed_single_in.setReadOnly(True)
        self.ed_single_in.setPlaceholderText("拖入图片后显示路径")
        btn_pick_file = QPushButton("选择文件")
        btn_pick_file.clicked.connect(self._pick_single_file)
        row_in.addWidget(btn_pick_file)
        row_in.addWidget(self.ed_single_in, 1)

        row_out = QHBoxLayout()
        self.ed_single_out = QLineEdit()
        self.ed_single_out.setReadOnly(True)
        self.ed_single_out.setPlaceholderText("默认：输入文件所在目录")
        btn_pick_out = QPushButton("选择输出文件夹")
        btn_pick_out.clicked.connect(self._pick_single_out_dir)
        row_out.addWidget(btn_pick_out)
        row_out.addWidget(self.ed_single_out, 1)

        self.cb_open_out = QCheckBox("完成后自动打开输出文件夹")
        self.cb_open_out.setChecked(True)

        single_layout.addWidget(self.drop)
        single_layout.addLayout(row_in)
        single_layout.addLayout(row_out)
        single_layout.addWidget(self.cb_open_out)

        layout.addWidget(lbl_mode, 0, 0)
        layout.addWidget(self.cb_mode, 0, 1)
        layout.addWidget(lbl_func, 1, 0)
        layout.addWidget(self.cb_func, 1, 1)
        layout.addWidget(self.stack, 2, 0, 1, 2)
        layout.addWidget(self.gb_single, 3, 0, 1, 2)

        self.cb_func.currentIndexChanged.connect(self.stack.setCurrentIndex)
        self.cb_mode.currentIndexChanged.connect(self._sync_mode)
        self._sync_mode()

    def _sync_mode(self) -> None:
        is_single = self.cb_mode.currentText().startswith("单文件")
        self.gb_single.setVisible(is_single)

    def _on_file_dropped(self, path: str) -> None:
        self.ed_single_in.setText(path)

    def _pick_single_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff)",
        )
        if path:
            self.ed_single_in.setText(path)

    def _pick_single_out_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if path:
            self.ed_single_out.setText(path)

    def get_active_task_id(self) -> str:
        text = self.cb_func.currentText().strip()
        if text == "尺寸调整":
            return "image.resize"
        if text == "格式转换":
            return "image.convert"
        return "image.resize_convert"

    def get_params(self) -> dict:
        active = self.get_active_task_id()

        if active == "image.resize":
            base = self.page_resize_single.get_params()
        elif active == "image.convert":
            base = self.page_convert_single.get_params()
        else:
            base = {}
            base.update(self.page_resize_combo.get_params())
            base.update(self.page_convert_combo.get_params())

        mode = "single" if self.cb_mode.currentText().startswith("单文件") else "batch"

        single_file = self.ed_single_in.text().strip()
        out_dir = self.ed_single_out.text().strip()
        if not out_dir and single_file:
            out_dir = str(Path(single_file).parent)

        base.update(
            {
                "image_mode": mode,
                "single_file": single_file,
                "single_out_dir": out_dir,
                "open_out_dir": bool(self.cb_open_out.isChecked()),
            }
        )
        return base
