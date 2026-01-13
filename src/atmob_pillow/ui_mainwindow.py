from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QProgressBar,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .tasks.registry import list_task_infos
from .ui.tool_audio_convert import AudioConvertToolWidget
from .ui.tool_image_resize import ImageResizeToolWidget
from .ui.tool_midi_to_xml import MidiToXmlToolWidget
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
QListWidget {
  border: 1px solid #d9d9d9;
  border-radius: 10px;
  padding: 6px;
  background: #ffffff;
}
QListWidget::item {
  padding: 10px 10px;
  border-radius: 8px;
}
QListWidget::item:selected {
  background: #e6f4ff;
  color: #0958d9;
}
"""


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("星檬-工具箱")
        self.resize(980, 680)

        self._worker: Worker | None = None

        self._task_infos = list_task_infos()
        self._task_id_by_row: list[str] = []
        self._page_index_by_task_id: dict[str, int] = {}

        root = QWidget(self)
        self.setCentralWidget(root)

        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(10)

        title = QLabel("星檬-AI中台工具箱")
        f = QFont()
        f.setPointSize(16)
        f.setBold(True)
        title.setFont(f)
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        main_layout.addWidget(title)

        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter, 1)

        # 左侧：工具列表
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        left_title = QLabel("工具")
        left_title_font = QFont()
        left_title_font.setBold(True)
        left_title.setFont(left_title_font)
        left_layout.addWidget(left_title)

        self.list_tools = QListWidget()
        left_layout.addWidget(self.list_tools, 1)

        splitter.addWidget(left)

        # 右侧：内容
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # 输入/输出
        gb_io = QGroupBox("输入/输出")
        io_layout = QHBoxLayout(gb_io)
        io_layout.setContentsMargins(14, 16, 14, 14)
        io_layout.setSpacing(10)

        col1 = QWidget()
        col1_layout = QVBoxLayout(col1)
        col1_layout.setContentsMargins(0, 0, 0, 0)
        col1_layout.setSpacing(8)

        row_in = QWidget()
        row_in_layout = QHBoxLayout(row_in)
        row_in_layout.setContentsMargins(0, 0, 0, 0)
        row_in_layout.setSpacing(10)
        self.btn_pick_input = QPushButton("选择输入文件夹")
        self.ed_input = QLineEdit()
        self.ed_input.setReadOnly(True)
        self.ed_input.setPlaceholderText("请选择输入文件夹")
        row_in_layout.addWidget(self.btn_pick_input)
        row_in_layout.addWidget(self.ed_input, 1)

        row_out = QWidget()
        row_out_layout = QHBoxLayout(row_out)
        row_out_layout.setContentsMargins(0, 0, 0, 0)
        row_out_layout.setSpacing(10)
        self.btn_pick_output = QPushButton("选择输出文件夹")
        self.ed_output = QLineEdit()
        self.ed_output.setReadOnly(True)
        self.ed_output.setPlaceholderText("未选择时：默认输出到程序所在目录")
        row_out_layout.addWidget(self.btn_pick_output)
        row_out_layout.addWidget(self.ed_output, 1)

        col1_layout.addWidget(row_in)
        col1_layout.addWidget(row_out)

        io_layout.addWidget(col1, 1)
        right_layout.addWidget(gb_io)

        # 参数区：根据工具切换页面
        self.gb_params = QGroupBox("参数")
        params_outer = QVBoxLayout(self.gb_params)
        params_outer.setContentsMargins(14, 16, 14, 14)
        params_outer.setSpacing(10)

        self.params_stack = QStackedWidget()
        params_outer.addWidget(self.params_stack)

        # 页面：图片
        self.image_resize_widget = ImageResizeToolWidget()
        idx_img = self.params_stack.addWidget(self.image_resize_widget)
        self._page_index_by_task_id["image.resize"] = idx_img

        # 页面：音频
        self.audio_convert_widget = AudioConvertToolWidget()
        idx_audio = self.params_stack.addWidget(self.audio_convert_widget)
        self._page_index_by_task_id["audio.convert"] = idx_audio

        # 页面：MIDI
        self.midi_to_xml_widget = MidiToXmlToolWidget()
        idx_midi = self.params_stack.addWidget(self.midi_to_xml_widget)
        self._page_index_by_task_id["midi.to_xml"] = idx_midi

        right_layout.addWidget(self.gb_params)

        # 控制
        gb_ctrl = QGroupBox("控制")
        ctrl_layout = QHBoxLayout(gb_ctrl)
        ctrl_layout.setContentsMargins(14, 16, 14, 14)
        self.btn_start = QPushButton("开始")
        self.btn_start.setObjectName("StartButton")
        self.btn_start.setMinimumHeight(36)
        ctrl_layout.addStretch(1)
        ctrl_layout.addWidget(self.btn_start)
        ctrl_layout.addStretch(1)
        right_layout.addWidget(gb_ctrl)

        # 状态
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

        right_layout.addWidget(gb_status, 1)

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([220, 760])

        # 工具列表：来自 registry
        for info in self._task_infos:
            self.list_tools.addItem(info.name)
            self._task_id_by_row.append(info.task_id)

        if self.list_tools.count() > 0:
            # 默认选中音频转换
            audio_task_id = "audio.convert"
            if audio_task_id in self._task_id_by_row:
                self.list_tools.setCurrentRow(self._task_id_by_row.index(audio_task_id))
            else:
                self.list_tools.setCurrentRow(0)
            self._sync_params_page()

        # signals
        self.btn_pick_input.clicked.connect(self.pick_input_dir)
        self.btn_pick_output.clicked.connect(self.pick_output_dir)
        self.btn_start.clicked.connect(self.start_work)
        self.list_tools.currentRowChanged.connect(lambda _: self._sync_params_page())

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

    def _current_task_id(self) -> str:
        row = self.list_tools.currentRow()
        if 0 <= row < len(self._task_id_by_row):
            return self._task_id_by_row[row]
        return ""

    def _sync_params_page(self) -> None:
        task_id = self._current_task_id()
        idx = self._page_index_by_task_id.get(task_id)
        if idx is not None:
            self.params_stack.setCurrentIndex(idx)

    def start_work(self) -> None:
        if self._worker and self._worker.isRunning():
            QMessageBox.information(self, "提示", "正在处理中，请等待完成。")
            return

        task_id = self._current_task_id()
        if not task_id:
            QMessageBox.warning(self, "提示", "请选择一个工具。")
            return

        input_dir = self.ed_input.text().strip()
        if not input_dir:
            QMessageBox.warning(self, "提示", "请先选择输入文件夹。")
            return

        output_dir = self.ed_output.text().strip()
        if not output_dir:
            output_dir = str(Path.cwd())

        # 根据工具获取参数 + 校验
        if task_id == "image.resize":
            params = self.image_resize_widget.get_params()
            if params.get("target_w", 0) <= 0 and params.get("target_h", 0) <= 0:
                QMessageBox.warning(self, "提示", "请至少设置宽度或高度其中一个（0 表示不限制）。")
                return
        elif task_id == "audio.convert":
            params = self.audio_convert_widget.get_params()

            start = params.get("cut_start", "")
            end = params.get("cut_end", "")
            if (start and not end) or (end and not start):
                QMessageBox.warning(self, "提示", "剪切需要同时填写开始和结束时间，或两者都留空。")
                return
        elif task_id == "midi.to_xml":
            params = self.midi_to_xml_widget.get_params()
        else:
            QMessageBox.warning(self, "提示", "未实现的工具。")
            return

        # 日志
        self.log.clear()
        self._append_log(f"工具: {self.list_tools.currentItem().text() if self.list_tools.currentItem() else task_id}")
        self._append_log(f"输入: {input_dir}")
        self._append_log(f"输出: {output_dir}")

        if task_id == "image.resize":
            self._append_log(
                f"参数: width={params['target_w']}, height={params['target_h']}, quality={params['quality']}"
            )
        elif task_id == "audio.convert":
            codec = params.get("audio_codec") or "自动"
            channels = params.get("channels") or "自动"
            sr = params.get("sample_rate_hz") or "自动"
            br = params.get("bitrate_kbps")
            br_str = "无更改" if not br else f"{br}KBPS"
            vol = params.get("volume_db") or "无更改"
            cut_start = params.get("cut_start") or ""
            cut_end = params.get("cut_end") or ""
            cut_str = "无" if not (cut_start or cut_end) else f"{cut_start}-{cut_end}"

            self._append_log(
                "参数: "
                f"format={params['output_format']}, "
                f"codec={codec}, "
                f"channels={channels}, "
                f"sr={sr}, "
                f"bitrate={br_str}, "
                f"volume={vol}, "
                f"cut={cut_str}"
            )
        elif task_id == "midi.to_xml":
            self._append_log("参数: 无")

        self.btn_start.setEnabled(False)
        self.btn_pick_input.setEnabled(False)
        self.btn_pick_output.setEnabled(False)
        self.list_tools.setEnabled(False)

        self._worker = Worker(
            task_id=task_id,
            params=params,
            input_dir=input_dir,
            output_dir=output_dir,
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
        self.list_tools.setEnabled(True)
        self._append_log("任务结束")
