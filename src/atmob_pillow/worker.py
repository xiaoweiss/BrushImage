from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from .tasks.registry import list_task_infos


class Worker(QThread):
    progress_changed = Signal(int, int)  # processed, total
    log = Signal(str)
    finished_ok = Signal()

    def __init__(
        self,
        task_id: str,
        params: dict,
        input_dir: str,
        output_dir: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._task_id = task_id
        self._params = dict(params)
        self._input_dir = input_dir
        self._output_dir = output_dir

    def _create_task(self):
        for info in list_task_infos():
            if info.task_id == self._task_id:
                return info.factory()
        return None

    def run(self) -> None:
        task = self._create_task()
        if task is None:
            self.log.emit(f"未知工具: {self._task_id}")
            self.finished_ok.emit()
            return

        # 参数直接塞到对象上（保持简单）
        for k, v in self._params.items():
            if hasattr(task, k):
                setattr(task, k, v)

        concurrency = int(self._params.get("concurrency", 1) or 1)
        concurrency = max(1, min(32, concurrency))

        in_dir = Path(self._input_dir)
        out_dir = Path(self._output_dir)

        if not in_dir.exists() or not in_dir.is_dir():
            self.log.emit(f"输入文件夹无效: {in_dir}")
            self.finished_ok.emit()
            return

        out_dir.mkdir(parents=True, exist_ok=True)

        candidates = [p for p in in_dir.iterdir() if p.is_file()]
        if hasattr(task, "accept_file") and callable(getattr(task, "accept_file")):
            candidates = [p for p in candidates if task.accept_file(p)]

        total = len(candidates)
        processed = 0

        self.log.emit(f"开始扫描: {in_dir} (共 {total} 个文件), 并发数={concurrency}")
        self.progress_changed.emit(0, total)

        def _run_one(p: Path):
            try:
                result = task.process_one(p, out_dir)
                msg = getattr(result, "message", str(result))
                return True, msg
            except Exception as e:
                return False, f"失败: {p.name} ({e})"

        if concurrency <= 1:
            for p in candidates:
                ok, msg = _run_one(p)
                self.log.emit(msg)
                processed += 1
                self.progress_changed.emit(processed, total)
        else:
            # 线程池并发：适用于 ffmpeg 子进程任务；MIDI/music21 若有线程安全问题可将并发数设为 1
            with ThreadPoolExecutor(max_workers=concurrency) as ex:
                future_to_path = {ex.submit(_run_one, p): p for p in candidates}
                for fut in as_completed(future_to_path):
                    ok, msg = fut.result()
                    self.log.emit(msg)
                    processed += 1
                    self.progress_changed.emit(processed, total)

        self.log.emit("全部处理完成")
        self.finished_ok.emit()
