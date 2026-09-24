import sys

from PySide6.QtWidgets import QApplication  # pylint: disable=no-name-in-module

from app.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("SupportFlow AI")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
