from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QWidget,
)


OUTPUT_FORMATS = [
    "SOU",
    "TTA",
    "VOC",
    "8SVX",
    "AU",
    "NIST",
    "IRCAM",
    "CAF",
    "FLAC",
    "APE",
    "WV",
    "SHN",
    "ALAC",
    "M4A",
    "M4R",
    "SPX",
    "GSM",
    "AMR",
    "QCP",
    "VOX",
    "WMA",
    "OGG",
    "AAC",
    "AC3",
    "DTS",
    "WAV",
    "MP3",
    "AIFF",
]


class AudioConvertToolWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)

        # 剪切
        lbl_cut = QLabel("剪切")
        cut_row = QWidget()
        cut_row_layout = QHBoxLayout(cut_row)
        cut_row_layout.setContentsMargins(0, 0, 0, 0)
        cut_row_layout.setSpacing(8)

        self.ed_cut_start = QLineEdit()
        self.ed_cut_start.setPlaceholderText("时:分:秒 (可选)")
        dash = QLabel("-")
        dash.setFixedWidth(10)
        self.ed_cut_end = QLineEdit()
        self.ed_cut_end.setPlaceholderText("时:分:秒 (可选)")

        cut_row_layout.addWidget(self.ed_cut_start)
        cut_row_layout.addWidget(dash)
        cut_row_layout.addWidget(self.ed_cut_end)

        # 输出格式
        lbl_format = QLabel("输出格式")
        self.cb_format = QComboBox()
        self.cb_format.addItems(OUTPUT_FORMATS)
        # 默认选中 MP3
        self.cb_format.setCurrentText("MP3")

        # 编解码器
        lbl_codec = QLabel("编解码器")
        self.cb_codec = QComboBox()
        self.cb_codec.addItem("自动(无更改)", "")
        self.cb_codec.addItem("MP3 (libmp3lame)", "libmp3lame")
        self.cb_codec.addItem("AAC", "aac")
        self.cb_codec.addItem("FLAC", "flac")
        self.cb_codec.addItem("PCM_ALaw, G.711 (未压缩)", "pcm_alaw")
        self.cb_codec.addItem("PCM_uLaw, G.711 (未压缩)", "pcm_mulaw")
        self.cb_codec.addItem("PCM_S16LE (未压缩)", "pcm_s16le")
        self.cb_codec.addItem("PCM_S24LE (未压缩)", "pcm_s24le")
        self.cb_codec.addItem("PCM_S32LE (未压缩)", "pcm_s32le")
        # 默认选择 PCM_S16LE
        self.cb_codec.setCurrentText("PCM_S16LE (未压缩)")

        # 声道
        # 编解码器
        lbl_codec = QLabel("编解码器")
        self.cb_codec = QComboBox()
        self.cb_codec.addItem("自动(无更改)", "")
        self.cb_codec.addItem("MP3 (libmp3lame)", "libmp3lame")
        self.cb_codec.addItem("AAC", "aac")
        self.cb_codec.addItem("FLAC", "flac")
        self.cb_codec.addItem("PCM_ALaw, G.711 (未压缩)", "pcm_alaw")
        self.cb_codec.addItem("PCM_uLaw, G.711 (未压缩)", "pcm_mulaw")
        self.cb_codec.addItem("PCM_S16LE (未压缩)", "pcm_s16le")
        self.cb_codec.addItem("PCM_S24LE (未压缩)", "pcm_s24le")
        self.cb_codec.addItem("PCM_S32LE (未压缩)", "pcm_s32le")

        # 声道
        lbl_channels = QLabel("音频声道")
        self.cb_channels = QComboBox()
        self.cb_channels.addItem("自动(无更改)", 0)
        self.cb_channels.addItem("单声道 (1.0)", 1)
        self.cb_channels.addItem("立体声 (2.0)", 2)
        self.cb_channels.addItem("2.1", 3)
        self.cb_channels.addItem("四声道 (4.0)", 4)
        self.cb_channels.addItem("5.0", 5)
        self.cb_channels.addItem("5.1", 6)
        self.cb_channels.addItem("7.0", 7)
        self.cb_channels.addItem("7.1", 8)

        # 频率(采样率)
        lbl_sr = QLabel("频率")
        self.cb_sample_rate = QComboBox()
        self.cb_sample_rate.addItem("自动(无更改)", 0)
        for hz in [8000, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000, 88200, 96000, 192000]:
            self.cb_sample_rate.addItem(f"{hz} Hz", hz)

        # 码率
        lbl_bitrate = QLabel("码率")
        bitrate_row = QWidget()
        bitrate_row_layout = QHBoxLayout(bitrate_row)
        bitrate_row_layout.setContentsMargins(0, 0, 0, 0)
        bitrate_row_layout.setSpacing(8)

        self.sp_bitrate = QSpinBox()
        self.sp_bitrate.setRange(0, 10000)
        self.sp_bitrate.setValue(0)
        self.sp_bitrate.setSpecialValueText("无更改")

        unit = QLabel("KBPS")
        unit.setMinimumWidth(44)

        bitrate_row_layout.addWidget(self.sp_bitrate)
        bitrate_row_layout.addWidget(unit)
        bitrate_row_layout.addStretch(1)

        # 音量
        lbl_volume = QLabel("音量")
        self.cb_volume = QComboBox()
        self.cb_volume.addItem("无更改", "")
        for db in [-90, -80, -70, -60, -50, -40, -30, -20, -10]:
            self.cb_volume.addItem(f"{db} dB", f"{db}dB")

        # 并发数
        lbl_conc = QLabel("并发数")
        self.sp_concurrency = QSpinBox()
        self.sp_concurrency.setRange(1, 32)
        self.sp_concurrency.setValue(1)

        layout.addWidget(lbl_cut, 0, 0)
        layout.addWidget(cut_row, 0, 1)
        layout.addWidget(lbl_format, 1, 0)
        layout.addWidget(self.cb_format, 1, 1)
        layout.addWidget(lbl_codec, 2, 0)
        layout.addWidget(self.cb_codec, 2, 1)
        layout.addWidget(lbl_channels, 3, 0)
        layout.addWidget(self.cb_channels, 3, 1)
        layout.addWidget(lbl_sr, 4, 0)
        layout.addWidget(self.cb_sample_rate, 4, 1)
        layout.addWidget(lbl_bitrate, 5, 0)
        layout.addWidget(bitrate_row, 5, 1)
        layout.addWidget(lbl_volume, 6, 0)
        layout.addWidget(self.cb_volume, 6, 1)
        layout.addWidget(lbl_conc, 7, 0)
        layout.addWidget(self.sp_concurrency, 7, 1)

    def get_params(self) -> dict:
        out_ext = self.cb_format.currentText().strip().lower()
        return {
            "output_format": out_ext,
            "audio_codec": str(self.cb_codec.currentData() or ""),
            "channels": int(self.cb_channels.currentData() or 0),
            "bitrate_kbps": int(self.sp_bitrate.value()),
            "sample_rate_hz": int(self.cb_sample_rate.currentData() or 0),
            "volume_db": str(self.cb_volume.currentData() or ""),
            "cut_start": self.ed_cut_start.text().strip(),
            "cut_end": self.ed_cut_end.text().strip(),
            "concurrency": int(self.sp_concurrency.value()),
        }
