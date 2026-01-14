from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from .tasks.registry import create_task


class Worker(QThread):
    progress_changed = Signal(int, int)  # processed, total
    log = Signal(str)
    finished_ok = Signal(str)  # output_dir

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

    def run(self) -> None:
        task = create_task(self._task_id, self._params)
        if task is None:
            self.log.emit(f"未知工具或参数不完整: {self._task_id}")
            self.finished_ok.emit(self._output_dir)
            return

        # 参数塞到 task 对象上
        for k, v in self._params.items():
            if hasattr(task, k):
                setattr(task, k, v)

        concurrency = int(self._params.get("concurrency", 1) or 1)
        concurrency = max(1, min(32, concurrency))

        out_dir = Path(self._output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        mode = (self._params.get("image_mode") or "batch").lower()
        single_file = (self._params.get("single_file") or "").strip()

        # 单文件模式
        if mode == "single" and single_file:
            p = Path(single_file)
            if not p.exists() or not p.is_file():
                self.log.emit(f"输入文件无效: {p}")
                self.finished_ok.emit(str(out_dir))
                return

            self.progress_changed.emit(0, 1)
            try:
                result = task.process_one(p, out_dir)
                msg = getattr(result, "message", str(result))
                self.log.emit(msg)
            except Exception as e:
                self.log.emit(f"失败: {p.name} ({e})")
            self.progress_changed.emit(1, 1)
            self.log.emit("全部处理完成")
            self.finished_ok.emit(str(out_dir))
            return

        # 批量模式
        in_dir = Path(self._input_dir)
        if not in_dir.exists() or not in_dir.is_dir():
            self.log.emit(f"输入文件夹无效: {in_dir}")
            self.finished_ok.emit(str(out_dir))
            return

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
                return msg
            except Exception as e:
                return f"失败: {p.name} ({e})"

        if concurrency <= 1:
            for p in candidates:
                msg = _run_one(p)
                self.log.emit(msg)
                processed += 1
                self.progress_changed.emit(processed, total)
        else:
            with ThreadPoolExecutor(max_workers=concurrency) as ex:
                futures = [ex.submit(_run_one, p) for p in candidates]
                for fut in as_completed(futures):
                    msg = fut.result()
                    self.log.emit(msg)
                    processed += 1
                    self.progress_changed.emit(processed, total)

        self.log.emit("全部处理完成")
        self.finished_ok.emit(str(out_dir))
