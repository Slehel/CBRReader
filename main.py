import sys
from PyQt6.QtWidgets import QApplication
from src.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()

    def on_exit():
        window.reader_view.cleanup()

    app.aboutToQuit.connect(on_exit)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
