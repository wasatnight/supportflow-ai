import sys
from pathlib import Path

from PySide6.QtGui import QIcon  # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QApplication  # pylint: disable=no-name-in-module

from app.main_window import MainWindow


def resource_path(relative_path: str) -> Path:
    base_path = Path(
        getattr(
            sys,
            "_MEIPASS",
            Path(__file__).resolve().parents[2],
        )
    )
    return base_path / relative_path


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("SupportFlow AI")

    app_icon = QIcon(str(resource_path("assets/SupportFlowAI.ico")))
    app.setWindowIcon(app_icon)

    window = MainWindow()
    window.setWindowIcon(app_icon)
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
