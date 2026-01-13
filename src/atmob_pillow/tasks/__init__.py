from __future__ import annotations

from .image_resize import ImageResizeTask


def list_tasks() -> list[object]:
    return [
        ImageResizeTask(),
    ]
