from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class TaskResult:
    success: bool
    message: str
    output_path: Optional[Path] = None


class MidiToXmlTask:
    id = "midi.to_xml"
    name = "MIDI 转 MusicXML"
    description = "将 MIDI 文件转换为 MusicXML (.xml)（依赖 music21）"

    def accept_file(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in {".mid", ".midi"}

    def process_one(self, input_path: Path, output_dir: Path) -> TaskResult:
        try:
            import music21  # 延迟导入，避免未安装时影响其它工具
        except Exception:
            return TaskResult(False, "未安装 music21：请先执行 uv pip install music21", None)

        try:
            out_dir = Path(output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)

            out_path = out_dir / f"{input_path.stem}.musicxml"
            if out_path.exists():
                return TaskResult(True, f"跳过(已存在): {out_path.name}", out_path)

            score = music21.converter.parse(str(input_path))
            score.write("musicxml", fp=str(out_path))

            return TaskResult(True, f"成功: {input_path.name} -> {out_path.name}", out_path)

        except Exception as e:
            return TaskResult(False, f"失败: {input_path.name} ({e})", None)
