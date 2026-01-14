from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .audio_convert import AudioConvertTask
from .image_convert import ImageConvertTask
from .image_resize import ImageResizeTask
from .midi_to_xml import MidiToXmlTask


@dataclass(frozen=True)
class TaskInfo:
    task_id: str
    name: str
    factory: Callable[[], object]


def list_task_infos() -> list[TaskInfo]:
    return [
        TaskInfo(task_id="image.tools", name="图片工具", factory=lambda: object()),
        TaskInfo(task_id=AudioConvertTask.id, name=AudioConvertTask.name, factory=AudioConvertTask),
        TaskInfo(task_id=MidiToXmlTask.id, name=MidiToXmlTask.name, factory=MidiToXmlTask),
    ]


def create_task(task_id: str, params: dict):
    """用于 Worker 创建真正可执行的 task。

    - UI 层的 image.tools 是一个“组合工具”，在这里根据 params['active_task_id'] 分发到 image.resize/image.convert。
    """

    if task_id == "image.tools":
        active = (params.get("active_task_id") or "").strip()
        if active == "image.resize":
            return ImageResizeTask()
        if active == "image.convert":
            return ImageConvertTask()
        return None

    if task_id == AudioConvertTask.id:
        return AudioConvertTask()

    if task_id == MidiToXmlTask.id:
        return MidiToXmlTask()

    return None
