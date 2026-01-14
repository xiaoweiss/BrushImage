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


def _resize_image(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    w, h = img.size
    tw = int(target_w)
    th = int(target_h)

    if tw > 0 and th > 0:
        if (w, h) != (tw, th):
            return img.resize((tw, th), resample=Image.LANCZOS)
        return img
    if tw > 0 and th <= 0:
        new_h = max(1, int(round(h * (tw / float(w)))))
        return img.resize((tw, new_h), resample=Image.LANCZOS)
    if th > 0 and tw <= 0:
        new_w = max(1, int(round(w * (th / float(h)))))
        return img.resize((new_w, th), resample=Image.LANCZOS)
    return img


class ImageResizeConvertTask:
    id = "image.resize_convert"
    name = "尺寸调整+格式转换"
    description = "先调整尺寸（可拉伸）再转换格式（Pillow），支持透明 PNG 转 JPG 白底处理"

    def __init__(self) -> None:
        # resize 参数
        self.target_w: int = 0
        self.target_h: int = 0

        # convert 参数
        self.output_format: str = "jpg"  # jpg/png/webp
        self.quality: int = 90

    def accept_file(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}

    def _build_output_path(self, input_path: Path, output_dir: Path) -> Path:
        out_ext = _normalize_ext(self.output_format)
        if out_ext == ".jpeg":
            out_ext = ".jpg"
        # A1：包含源扩展名，避免冲突
        return Path(output_dir) / f"{input_path.name}_resized_converted{out_ext}"

    def process_one(self, input_path: Path, output_dir: Path) -> TaskResult:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        out_path = self._build_output_path(input_path, out_dir)
        if out_path.exists():
            return TaskResult(True, f"跳过(已存在): {out_path.name}", out_path)

        try:
            with Image.open(input_path) as img:
                # resize
                img = _resize_image(img, self.target_w, self.target_h)

                out_ext = out_path.suffix.lower()
                save_kwargs: dict = {}

                if out_ext in {".jpg", ".jpeg"}:
                    # PNG 透明 -> JPG 白底
                    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        if img.mode == "P":
                            img = img.convert("RGBA")
                        background.paste(img, mask=img.split()[-1])
                        img = background
                    else:
                        img = img.convert("RGB")

                    save_kwargs["quality"] = int(self.quality)
                    save_kwargs["optimize"] = True

                elif out_ext == ".png":
                    q = int(self.quality)
                    compress_level = int(round((100 - q) * 9 / 99))
                    compress_level = max(0, min(9, compress_level))
                    save_kwargs["compress_level"] = compress_level
                    save_kwargs["optimize"] = True

                elif out_ext == ".webp":
                    save_kwargs["quality"] = int(self.quality)

                img.save(out_path, **save_kwargs)

            return TaskResult(True, f"成功: {input_path.name} -> {out_path.name}", out_path)

        except Exception as e:
            return TaskResult(False, f"失败: {input_path.name} ({e})", None)
