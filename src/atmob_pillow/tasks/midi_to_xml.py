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
    description = "将 MIDI 文件转换为 MusicXML (.musicxml)（依赖 music21）"

    def __init__(self) -> None:
        self.quantize_mode: str = "auto"  # off/auto/1/8/1/16/1/32
        self.remove_tiny_rests: bool = False

    def accept_file(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in {".mid", ".midi"}

    def process_one(self, input_path: Path, output_dir: Path) -> TaskResult:
        try:
            import music21
        except Exception:
            return TaskResult(False, "未安装 music21：请先执行 uv pip install music21", None)

        try:
            out_dir = Path(output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)

            out_path = out_dir / f"{input_path.stem}.musicxml"
            if out_path.exists():
                return TaskResult(True, f"跳过(已存在): {out_path.name}", out_path)

            score = music21.converter.parse(str(input_path))

            mode = (self.quantize_mode or "off").lower()

            if mode != "off":
                if mode == "auto":
                    # 使用 music21 自带的自动量化逻辑（不指定网格）
                    for part in score.parts:
                        part.quantize(inPlace=True)
                else:
                    # 指定网格：以 quarterLength 表示
                    grid_map = {
                        "1/8": 0.5,
                        "1/16": 0.25,
                        "1/32": 0.125,
                    }
                    ql = grid_map.get(mode)
                    if ql is not None:
                        for part in score.parts:
                            part.quantize([ql], inPlace=True)

            # 去除小休止符：阈值 1/32 拍 = 0.125（quarterLength）
            if self.remove_tiny_rests:
                for part in score.parts:
                    elements_to_remove = []
                    for el in part.flatten().notesAndRests:
                        if isinstance(el, music21.note.Rest) and el.duration.quarterLength < 0.125:
                            elements_to_remove.append(el)
                    for el in elements_to_remove:
                        part.remove(el, recurse=True)

            score.write("musicxml", fp=str(out_path))

            return TaskResult(True, f"成功: {input_path.name} -> {out_path.name}", out_path)

        except Exception as e:
            return TaskResult(False, f"失败: {input_path.name} ({e})", None)
