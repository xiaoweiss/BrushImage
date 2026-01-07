from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QProgressBar,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .worker import Worker


APP_QSS = """
QWidget {
  font-family: "Segoe UI", "Microsoft YaHei UI", "PingFang SC", sans-serif;
  font-size: 13px;
}
QGroupBox {
  border: 1px solid #d9d9d9;
  border-radius: 10px;
  margin-top: 10px;
  background: #ffffff;
}
QGroupBox::title {
  subcontrol-origin: margin;
  left: 12px;
  padding: 0 6px;
  color: #333;
  font-weight: 600;
}
QLineEdit {
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  padding: 6px 10px;
  background: #fafafa;
}
QSpinBox {
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  padding: 6px 10px;
  background: #fafafa;
}
QSpinBox::up-button, QSpinBox::down-button {
  width: 0px;
  border: none;
}
QPushButton {
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  padding: 7px 14px;
  background: #f6f6f6;
}
QPushButton:hover { background: #ededed; }
QPushButton:pressed { background: #e6e6e6; }
QPushButton#StartButton {
  background: #1677ff;
  color: white;
  border: none;
  font-weight: 600;
}
QPushButton#StartButton:hover { background: #4096ff; }
QPushButton#StartButton:pressed { background: #0958d9; }
QProgressBar {
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  text-align: center;
  background: #fafafa;
  height: 18px;
}
QProgressBar::chunk {
  border-radius: 8px;
  background: #52c41a;
}
QPlainTextEdit {
  border: 1px solid #d9d9d9;
  border-radius: 10px;
  background: #0b1220;
  color: #d6e4ff;
  padding: 8px;
  font-family: "Consolas", "Menlo", monospace;
  font-size: 12px;
}
"""


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Atmob Pillow - 批量缩放")
        self.resize(820, 620)

        self._worker: Worker | None = None

        root = QWidget(self)
        self.setCentralWidget(root)

        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)

        title = QLabel("星檬-批量图片缩放工具")
        f = QFont()
        f.setPointSize(16)
        f.setBold(True)
        title.setFont(f)
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        main_layout.addWidget(title)

        # 输入区
        gb_io = QGroupBox("输入/输出")
        io_layout = QGridLayout(gb_io)
        io_layout.setContentsMargins(14, 16, 14, 14)
        io_layout.setHorizontalSpacing(10)
        io_layout.setVerticalSpacing(10)

        self.btn_pick_input = QPushButton("选择输入文件夹")
        self.ed_input = QLineEdit()
        self.ed_input.setReadOnly(True)
        self.ed_input.setPlaceholderText("请选择输入文件夹")

        self.btn_pick_output = QPushButton("选择输出文件夹")
        self.ed_output = QLineEdit()
        self.ed_output.setReadOnly(True)
        self.ed_output.setPlaceholderText("未选择时：默认输出到程序所在目录")

        io_layout.addWidget(self.btn_pick_input, 0, 0)
        io_layout.addWidget(self.ed_input, 0, 1)
        io_layout.addWidget(self.btn_pick_output, 1, 0)
        io_layout.addWidget(self.ed_output, 1, 1)

        main_layout.addWidget(gb_io)

        # 参数区
        gb_params = QGroupBox("参数")
        params_layout = QGridLayout(gb_params)
        params_layout.setContentsMargins(14, 16, 14, 14)
        params_layout.setHorizontalSpacing(10)
        params_layout.setVerticalSpacing(10)

        lbl_w = QLabel("目标宽度")
        self.sp_width = QSpinBox()
        self.sp_width.setRange(0, 20000)
        self.sp_width.setValue(0)

        lbl_h = QLabel("目标高度")
        self.sp_height = QSpinBox()
        self.sp_height.setRange(0, 20000)
        self.sp_height.setValue(0)

        lbl_q = QLabel("质量/压缩 (Quality，1-100)")
        self.sp_quality = QSpinBox()
        self.sp_quality.setRange(1, 100)
        self.sp_quality.setValue(100)

        params_layout.addWidget(lbl_w, 0, 0)
        params_layout.addWidget(self.sp_width, 0, 1)
        params_layout.addWidget(lbl_h, 1, 0)
        params_layout.addWidget(self.sp_height, 1, 1)
        params_layout.addWidget(lbl_q, 2, 0)
        params_layout.addWidget(self.sp_quality, 2, 1)

        main_layout.addWidget(gb_params)

        # 控制区
        gb_ctrl = QGroupBox("控制")
        ctrl_layout = QHBoxLayout(gb_ctrl)
        ctrl_layout.setContentsMargins(14, 16, 14, 14)

        self.btn_start = QPushButton("开始")
        self.btn_start.setObjectName("StartButton")
        self.btn_start.setMinimumHeight(36)
        ctrl_layout.addStretch(1)
        ctrl_layout.addWidget(self.btn_start)
        ctrl_layout.addStretch(1)

        main_layout.addWidget(gb_ctrl)

        # 状态区
        gb_status = QGroupBox("状态")
        status_layout = QVBoxLayout(gb_status)
        status_layout.setContentsMargins(14, 16, 14, 14)
        status_layout.setSpacing(10)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFormat("0/0")

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)

        status_layout.addWidget(self.progress)
        status_layout.addWidget(self.log, 1)

        main_layout.addWidget(gb_status, 1)

        # signals
        self.btn_pick_input.clicked.connect(self.pick_input_dir)
        self.btn_pick_output.clicked.connect(self.pick_output_dir)
        self.btn_start.clicked.connect(self.start_work)

    def apply_style(self) -> None:
        self.setStyleSheet(APP_QSS)

    def pick_input_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "选择输入文件夹")
        if path:
            self.ed_input.setText(path)

    def pick_output_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if path:
            self.ed_output.setText(path)

    def _append_log(self, text: str) -> None:
        self.log.appendPlainText(text)
        sb = self.log.verticalScrollBar()
        sb.setValue(sb.maximum())

    def start_work(self) -> None:
        if self._worker and self._worker.isRunning():
            QMessageBox.information(self, "提示", "正在处理中，请等待完成。")
            return

        input_dir = self.ed_input.text().strip()
        if not input_dir:
            QMessageBox.warning(self, "提示", "请先选择输入文件夹。")
            return

        output_dir = self.ed_output.text().strip()
        if not output_dir:
            # 未选输出：默认输出到程序所在目录
            output_dir = str(Path.cwd())

        target_w = int(self.sp_width.value())
        target_h = int(self.sp_height.value())
        quality = int(self.sp_quality.value())

        if target_w <= 0 and target_h <= 0:
            QMessageBox.warning(self, "提示", "请至少设置宽度或高度其中一个（0 表示不限制）。")
            return

        self.log.clear()
        self._append_log(f"输入: {input_dir}")
        self._append_log(f"输出: {output_dir}")
        self._append_log(f"Width: {target_w}, Height: {target_h}, Quality: {quality}")

        self.btn_start.setEnabled(False)
        self.btn_pick_input.setEnabled(False)
        self.btn_pick_output.setEnabled(False)

        self._worker = Worker(
            input_dir=input_dir,
            output_dir=output_dir,
            target_w=target_w,
            target_h=target_h,
            quality=quality,
        )
        self._worker.progress_changed.connect(self.on_progress)
        self._worker.log.connect(self._append_log)
        self._worker.finished_ok.connect(self.on_finished)
        self._worker.start()

    def on_progress(self, processed: int, total: int) -> None:
        if total <= 0:
            self.progress.setRange(0, 1)
            self.progress.setValue(0)
            self.progress.setFormat("0/0")
            return

        self.progress.setRange(0, total)
        self.progress.setValue(processed)
        self.progress.setFormat(f"{processed}/{total}")

    def on_finished(self) -> None:
        self.btn_start.setEnabled(True)
        self.btn_pick_input.setEnabled(True)
        self.btn_pick_output.setEnabled(True)
        self._append_log("任务结束")
