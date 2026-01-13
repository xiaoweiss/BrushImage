from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..processor import process_one_image


@dataclass
class TaskResult:
    success: bool
    message: str
    output_path: Optional[Path] = None


class ImageResizeTask:
    id = "image.resize"
    name = "图片尺寸调整"
    description = "调整图片到指定尺寸（强制拉伸）"

    def __init__(self):
        self.target_w = 0
        self.target_h = 0
        self.quality = 100

    def accept_file(self, file_path: Path) -> bool:
        """判断是否处理该文件"""
        # 简单判断：检查文件扩展名
        return file_path.suffix.lower() in {
            ".jpg", ".jpeg", ".png", ".webp", ".bmp"
        }

    def process_one(self, input_path: Path, output_dir: Path) -> TaskResult:
        """处理单个文件"""
        result = process_one_image(
            input_path=input_path,
            output_dir=output_dir,
            target_w=self.target_w,
            target_h=self.target_h,
            quality=self.quality,
        )
        return TaskResult(
            success=result.ok,
            message=result.message,
            output_path=result.output_path,
        )

    def get_ui_params(self) -> dict:
        """返回UI参数配置"""
        return {
            "target_w": {"type": "int", "default": 0, "label": "目标宽度", "min": 0, "max": 10000},
            "target_h": {"type": "int", "default": 0, "label": "目标高度", "min": 0, "max": 10000},
            "quality": {"type": "int", "default": 100, "label": "图片质量", "min": 1, "max": 100, "suffix": "%"},
        }