from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .ui_mainwindow import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.apply_style()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":  # pragma: no cover
    main()
