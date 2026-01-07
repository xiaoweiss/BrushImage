from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread, Signal

from .processor import process_one_image


class Worker(QThread):
    progress_changed = Signal(int, int)  # processed, total
    log = Signal(str)
    finished_ok = Signal()

    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        target_w: int,
        target_h: int,
        quality: int,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._input_dir = input_dir
        self._output_dir = output_dir
        self._target_w = int(target_w)
        self._target_h = int(target_h)
        self._quality = int(quality)

    def run(self) -> None:
        in_dir = Path(self._input_dir)
        out_dir = Path(self._output_dir)

        if not in_dir.exists() or not in_dir.is_dir():
            self.log.emit(f"输入文件夹无效: {in_dir}")
            self.finished_ok.emit()
            return

        out_dir.mkdir(parents=True, exist_ok=True)

        # MVP：不递归，只扫描根目录；“图片就行” => 交给 Pillow 打开失败则当作非图片/坏文件
        candidates = [p for p in in_dir.iterdir() if p.is_file()]
        total = len(candidates)
        processed = 0

        self.log.emit(f"开始扫描: {in_dir} (共 {total} 个文件)")
        self.progress_changed.emit(0, total)

        for p in candidates:
            # 串行处理
            result = process_one_image(
                input_path=p,
                output_dir=out_dir,
                target_w=self._target_w,
                target_h=self._target_h,
                quality=self._quality,
            )

            # 无论成功/失败都算处理过一个文件（进度条语义：处理数/总数）
            processed += 1
            self.progress_changed.emit(processed, total)
            self.log.emit(result.message)

        self.log.emit("全部处理完成")
        self.finished_ok.emit()
