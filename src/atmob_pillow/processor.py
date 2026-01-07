from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image


@dataclass(frozen=True)
class ProcessResult:
    ok: bool
    message: str
    output_path: Path | None = None


def process_one_image(
    input_path: str | Path,
    output_dir: str | Path,
    target_w: int,
    target_h: int,
    quality: int,
) -> ProcessResult:
    """处理单张图片

    - 缩放：使用 LANCZOS 重采样。
      * target_w>0,target_h>0：强制拉伸到指定宽高（例如 3000x3000）
      * 仅 target_w>0：按宽缩放，高度按原比例计算
      * 仅 target_h>0：按高缩放，宽度按原比例计算
    - 输出：保持原扩展名，文件名加 _resized
    - 质量：不再仅限 JPEG，会尽量应用到支持 quality 的格式；不支持则忽略。
    """

    in_path = Path(input_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = in_path.stem
    suffix = in_path.suffix  # 保持原扩展名（含点）
    out_path = out_dir / f"{stem}_resized{suffix}"

    if out_path.exists():
        return ProcessResult(ok=True, message=f"跳过(已存在): {out_path.name}", output_path=out_path)

    try:
        with Image.open(in_path) as img:
            w, h = img.size

            tw = int(target_w)
            th = int(target_h)

            # 计算缩放比例：输出严格到指定宽高（会改变比例/拉伸），并使用 LANCZOS
            # 如果你希望“不拉伸、保持比例”，应改回 fit 逻辑（min 比例）
            if tw > 0 and th > 0:
                if (w, h) != (tw, th):
                    img = img.resize((tw, th), resample=Image.LANCZOS)
            elif tw > 0 >= th:
                # 只指定宽：按原比例计算高
                new_h = max(1, int(round(h * (tw / float(w)))))
                img = img.resize((tw, new_h), resample=Image.LANCZOS)
            elif th > 0 >= tw:
                # 只指定高：按原比例计算宽
                new_w = max(1, int(round(w * (th / float(h)))))
                img = img.resize((new_w, th), resample=Image.LANCZOS)

            suffix_lower = suffix.lower()
            save_kwargs: dict = {}

            q = int(quality)

            # 尽量对更多格式应用“质量/压缩”
            # - JPEG: quality + optimize
            # - WebP: quality
            # - PNG: Pillow 不用 quality，使用 compress_level(0-9)，这里做一个简单映射
            if suffix_lower in {".jpg", ".jpeg"}:
                save_kwargs["quality"] = q
                save_kwargs["optimize"] = True
            elif suffix_lower == ".webp":
                save_kwargs["quality"] = q
            elif suffix_lower == ".png":
                # quality(1-100) -> compress_level(9-0)
                compress_level = int(round((100 - q) * 9 / 99))
                compress_level = max(0, min(9, compress_level))
                save_kwargs["compress_level"] = compress_level
                save_kwargs["optimize"] = True
            else:
                # 其它格式：尝试传 quality（若不支持会在 except 中失败，因此这里不强行加）
                pass

            img.save(out_path, **save_kwargs)

        return ProcessResult(ok=True, message=f"成功: {in_path.name} -> {out_path.name}", output_path=out_path)

    except Exception as e:  # 单图失败不中断，由 Worker 捕获/记录
        return ProcessResult(ok=False, message=f"失败: {in_path.name} ({e})", output_path=None)
