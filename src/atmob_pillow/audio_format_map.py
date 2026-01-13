from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AudioFormatPreset:
    ext: str
    container: str | None = None
    codec: str | None = None


# 说明：
# - container/codec 用于给 ffmpeg 提供一个“更好用”的默认值
# - 用户在 UI 里手动选择了编解码器时，始终优先用户选择
# - 未列出的格式：默认不强制指定 container/codec，让 ffmpeg 自己决定
AUDIO_FORMAT_PRESETS: dict[str, AudioFormatPreset] = {
    "mp3": AudioFormatPreset(ext="mp3", container="mp3", codec="libmp3lame"),
    "wav": AudioFormatPreset(ext="wav", container="wav", codec="pcm_s16le"),
    "aiff": AudioFormatPreset(ext="aiff", container="aiff", codec="pcm_s16le"),
    "flac": AudioFormatPreset(ext="flac", container="flac", codec="flac"),
    "ogg": AudioFormatPreset(ext="ogg", container="ogg", codec=None),
    "spx": AudioFormatPreset(ext="spx", container="ogg", codec="libspeex"),
    "aac": AudioFormatPreset(ext="aac", container="adts", codec="aac"),
    "m4a": AudioFormatPreset(ext="m4a", container="ipod", codec="aac"),
    "m4r": AudioFormatPreset(ext="m4r", container="ipod", codec="aac"),
    "amr": AudioFormatPreset(ext="amr", container="amr", codec="libopencore_amrnb"),
    "gsm": AudioFormatPreset(ext="gsm", container="gsm", codec="libgsm"),
    "ac3": AudioFormatPreset(ext="ac3", container="ac3", codec="ac3"),
    "dts": AudioFormatPreset(ext="dts", container="dts", codec="dca"),
    "au": AudioFormatPreset(ext="au", container="au", codec=None),
    "caf": AudioFormatPreset(ext="caf", container="caf", codec=None),
}
