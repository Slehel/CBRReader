from PyQt6.QtWidgets import QApplication

DARK = """
QMainWindow, QWidget {
    background-color: #1a1a1a;
    color: #cccccc;
}
QToolBar {
    background-color: #2a2a2a;
    border-bottom: 1px solid #333333;
    spacing: 6px;
    padding: 4px;
}
QPushButton {
    background-color: #333333;
    color: #cccccc;
    border: 1px solid #444444;
    border-radius: 4px;
    padding: 4px 10px;
}
QPushButton:hover {
    background-color: #444444;
}
QLabel {
    color: #cccccc;
}
QLineEdit {
    background-color: #2a2a2a;
    color: #888888;
    border: 1px solid #444444;
    border-radius: 3px;
    padding: 2px 6px;
}
QScrollArea, QScrollBar {
    background-color: #1a1a1a;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background-color: #444444;
    border-radius: 3px;
}
QStatusBar {
    background-color: #2a2a2a;
    color: #666666;
}
QProgressBar {
    background-color: #333333;
    border: none;
    border-radius: 2px;
    height: 4px;
}
QProgressBar::chunk {
    background-color: #555555;
    border-radius: 2px;
}
"""

LIGHT = """
QMainWindow, QWidget {
    background-color: #f0f0f0;
    color: #222222;
}
QToolBar {
    background-color: #e0e0e0;
    border-bottom: 1px solid #cccccc;
    spacing: 6px;
    padding: 4px;
}
QPushButton {
    background-color: #dddddd;
    color: #222222;
    border: 1px solid #bbbbbb;
    border-radius: 4px;
    padding: 4px 10px;
}
QPushButton:hover {
    background-color: #cccccc;
}
QLabel {
    color: #222222;
}
QLineEdit {
    background-color: #ffffff;
    color: #555555;
    border: 1px solid #cccccc;
    border-radius: 3px;
    padding: 2px 6px;
}
QScrollArea, QScrollBar {
    background-color: #f0f0f0;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background-color: #bbbbbb;
    border-radius: 3px;
}
QStatusBar {
    background-color: #e0e0e0;
    color: #888888;
}
QProgressBar {
    background-color: #cccccc;
    border: none;
    border-radius: 2px;
    height: 4px;
}
QProgressBar::chunk {
    background-color: #888888;
    border-radius: 2px;
}
"""


class ThemeManager:
    def __init__(self):
        self._dark = True

    @property
    def is_dark(self) -> bool:
        return self._dark

    def toggle(self) -> None:
        self._dark = not self._dark
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(DARK if self._dark else LIGHT)

    def apply(self) -> None:
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(DARK if self._dark else LIGHT)

    def toggle_label(self) -> str:
        return "☀" if self._dark else "☾"
