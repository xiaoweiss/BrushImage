from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path


def open_folder(path: str | Path) -> None:
    p = Path(path)
    if not p.exists():
        return

    system = platform.system().lower()
    try:
        if system == "darwin":
            subprocess.Popen(["open", str(p)])
        elif system == "windows":
            os.startfile(str(p))  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", str(p)])
    except Exception:
        # 打开失败不影响主流程
        return
