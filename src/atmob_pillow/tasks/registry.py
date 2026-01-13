from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .audio_convert import AudioConvertTask
from .image_resize import ImageResizeTask
from .midi_to_xml import MidiToXmlTask


@dataclass(frozen=True)
class TaskInfo:
    task_id: str
    name: str
    factory: Callable[[], object]


def list_task_infos() -> list[TaskInfo]:
    return [
        TaskInfo(task_id=ImageResizeTask.id, name=ImageResizeTask.name, factory=ImageResizeTask),
        TaskInfo(task_id=AudioConvertTask.id, name=AudioConvertTask.name, factory=AudioConvertTask),
        TaskInfo(task_id=MidiToXmlTask.id, name=MidiToXmlTask.name, factory=MidiToXmlTask),
    ]
