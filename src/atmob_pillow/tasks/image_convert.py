from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PIL import Image


@dataclass
class TaskResult:
    success: bool
    message: str
    output_path: Optional[Path] = None


def _normalize_ext(ext: str) -> str:
    e = (ext or "").strip().lower()
    if not e:
        return ""
    if not e.startswith("."):
        e = "." + e
    return e


def _parse_custom_exts(raw: str) -> set[str]:
    exts: set[str] = set()
    for part in (raw or "").split(","):
        p = part.strip().lower()
        if not p:
            continue
        if not p.startswith("."):
            p = "." + p
        exts.add(p)
    return exts


class ImageConvertTask:
    id = "image.convert"
    name = "图片转换"
    description = "按后缀过滤并转换图片格式（Pillow），支持透明 PNG 转 JPG 白底处理"

    def __init__(self) -> None:
        self.input_filter_mode: str = "all"  # all/only_png/only_jpg/custom
        self.input_filter_custom: str = ""  # e.g. "png,jpg"

        self.output_format: str = "jpg"  # jpg/png/webp
        self.quality: int = 90  # 1-100

    def accept_file(self, file_path: Path) -> bool:
        suffix = file_path.suffix.lower()
        if suffix not in {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}:
            return False

        mode = (self.input_filter_mode or "all").lower()
        if mode == "only_png":
            return suffix == ".png"
        if mode == "only_jpg":
            return suffix in {".jpg", ".jpeg"}
        if mode == "custom":
            exts = _parse_custom_exts(self.input_filter_custom)
            return (not exts) or (suffix in exts)

        return True

    def _build_output_path(self, input_path: Path, output_dir: Path) -> Path:
        out_ext = _normalize_ext(self.output_format)
        if out_ext in {".jpeg"}:
            out_ext = ".jpg"
        return Path(output_dir) / f"{input_path.name}_converted{out_ext}"

    def process_one(self, input_path: Path, output_dir: Path) -> TaskResult:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        out_path = self._build_output_path(input_path, out_dir)
        if out_path.exists():
            return TaskResult(True, f"跳过(已存在): {out_path.name}", out_path)

        try:
            with Image.open(input_path) as img:
                out_ext = out_path.suffix.lower()
                save_kwargs: dict = {}

                # 透明 PNG -> JPG：白底合成
                if out_ext in {".jpg", ".jpeg"}:
                    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        if img.mode == "P":
                            img = img.convert("RGBA")
                        # alpha 通道
                        background.paste(img, mask=img.split()[-1])
                        img = background
                    else:
                        img = img.convert("RGB")

                    save_kwargs["quality"] = int(self.quality)
                    save_kwargs["optimize"] = True

                elif out_ext == ".png":
                    # PNG：用 compress_level 映射 quality(1-100)->(9-0)
                    q = int(self.quality)
                    compress_level = int(round((100 - q) * 9 / 99))
                    compress_level = max(0, min(9, compress_level))
                    save_kwargs["compress_level"] = compress_level
                    save_kwargs["optimize"] = True

                elif out_ext == ".webp":
                    save_kwargs["quality"] = int(self.quality)

                else:
                    # 其他格式：尽量直接保存
                    pass

                img.save(out_path, **save_kwargs)

            return TaskResult(True, f"成功: {input_path.name} -> {out_path.name}", out_path)

        except Exception as e:
            return TaskResult(False, f"失败: {input_path.name} ({e})", None)
