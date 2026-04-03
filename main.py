import sys
from PyQt6.QtWidgets import QApplication
from src.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()

    def on_exit():
        rv = getattr(window, "reader_view", None)
        if rv is not None:
            rv.cleanup()

    app.aboutToQuit.connect(on_exit)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
