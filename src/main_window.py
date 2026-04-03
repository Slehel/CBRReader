from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from src.theme import ThemeManager
from src.library_view import LibraryView
from src.reader_view import ReaderView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CBR Reader")
        self.resize(1024, 768)

        self.theme = ThemeManager()
        self.theme.apply()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.library_view = LibraryView(self)
        self.reader_view = ReaderView(self)

        self.stack.addWidget(self.library_view)   # index 0
        self.stack.addWidget(self.reader_view)    # index 1

    def show_library(self):
        self.reader_view.cleanup()
        self.stack.setCurrentIndex(0)

    def show_reader(self, cbr_path: str):
        self.reader_view.load_comic(cbr_path)
        self.stack.setCurrentIndex(1)
