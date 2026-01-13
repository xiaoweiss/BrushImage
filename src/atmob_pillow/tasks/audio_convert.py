from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from atmob_pillow.audio_format_map import AUDIO_FORMAT_PRESETS


AUDIO_EXTENSIONS = {
    ".sou",
    ".tta",
    ".voc",
    ".8svx",
    ".au",
    ".nist",
    ".ircam",
    ".caf",
    ".flac",
    ".ape",
    ".wv",
    ".shn",
    ".alac",
    ".m4a",
    ".m4r",
    ".spx",
    ".gsm",
    ".amr",
    ".qcp",
    ".vox",
    ".wma",
    ".ogg",
    ".aac",
    ".ac3",
    ".dts",
    ".wav",
    ".mp3",
    ".aiff",
}


@dataclass
class TaskResult:
    success: bool
    message: str
    output_path: Optional[Path] = None


class AudioConvertTask:
    id = "audio.convert"
    name = "音频转换"
    description = "音频格式互转（依赖 ffmpeg）"

    def __init__(self) -> None:
        self.output_format: str = "mp3"
        self.audio_codec: str = ""  # 空表示自动
        self.channels: int = 0  # 0 表示不指定
        self.bitrate_kbps: int = 0  # 0 表示不指定
        self.sample_rate_hz: int = 0  # 0 表示不指定
        self.volume_db: str = ""  # e.g. "-10dB"，空表示无更改
        self.cut_start: str = ""  # "HH:MM:SS" 或 "SS"，空表示无
        self.cut_end: str = ""  # "HH:MM:SS" 或 "SS"，空表示无

    def accept_file(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in AUDIO_EXTENSIONS

    def _build_output_path(self, input_path: Path, output_dir: Path) -> Path:
        out_ext = (self.output_format or "mp3").lower().lstrip(".")
        return Path(output_dir) / f"{input_path.stem}_converted.{out_ext}"

    def process_one(self, input_path: Path, output_dir: Path) -> TaskResult:
        if shutil.which("ffmpeg") is None:
            return TaskResult(False, "未找到 ffmpeg：请先安装并确保在 PATH 中", None)

        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        out_path = self._build_output_path(input_path, out_dir)
        if out_path.exists():
            return TaskResult(True, f"跳过(已存在): {out_path.name}", out_path)

        out_ext = out_path.suffix.lower().lstrip(".")
        preset = AUDIO_FORMAT_PRESETS.get(out_ext)

        cmd = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(input_path),
        ]

        # 剪切（精度优先，放在 -i 之后）
        if self.cut_start:
            cmd += ["-ss", self.cut_start]
        if self.cut_end:
            cmd += ["-to", self.cut_end]

        # 输出容器（推荐）
        if preset and preset.container:
            cmd += ["-f", preset.container]

        # 编码器：用户选了优先；否则使用推荐；否则不指定
        codec_to_use = self.audio_codec or (preset.codec if preset else "")
        if codec_to_use:
            cmd += ["-c:a", codec_to_use]

        # 声道/采样率/码率：只有用户设置才传
        if int(self.channels) > 0:
            cmd += ["-ac", str(int(self.channels))]
        if int(self.sample_rate_hz) > 0:
            cmd += ["-ar", str(int(self.sample_rate_hz))]
        if int(self.bitrate_kbps) > 0:
            cmd += ["-b:a", f"{int(self.bitrate_kbps)}k"]

        # 音量（dB）
        if self.volume_db:
            cmd += ["-filter:a", f"volume={self.volume_db}"]

        cmd.append(str(out_path))

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return TaskResult(True, f"成功: {input_path.name} -> {out_path.name}", out_path)
        except subprocess.CalledProcessError as e:
            err = (e.stderr or "").strip()
            msg = f"失败: {input_path.name}"
            if err:
                msg += f" ({err})"
            return TaskResult(False, msg, None)
