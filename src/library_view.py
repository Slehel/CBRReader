import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QToolBar,
    QPushButton, QLineEdit, QLabel, QScrollArea,
    QGridLayout, QFileDialog, QSizePolicy
)
from PyQt6.QtCore import Qt
from src.thumbnail_loader import ThumbnailLoader


class ThumbnailWidget(QWidget):
    def __init__(self, cbr_path: str, main_window, parent=None):
        super().__init__(parent)
        self.cbr_path = cbr_path
        self.main_window = main_window
        self.setFixedSize(100, 140)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.image_label = QLabel()
        self.image_label.setFixedSize(88, 110)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: #2a2a2a; border-radius: 2px;")

        name = os.path.basename(cbr_path)
        if len(name) > 14:
            name = name[:12] + "…"
        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("font-size: 9px;")

        layout.addWidget(self.image_label)
        layout.addWidget(self.name_label)

    def mouseDoubleClickEvent(self, event):
        if self.main_window:
            self.main_window.show_reader(self.cbr_path)


class LibraryView(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self._cbr_files: list[str] = []
        self._loaders: list[ThumbnailLoader] = []

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        open_btn = QPushButton("Open Folder")
        open_btn.clicked.connect(self._open_folder_dialog)
        self.path_display = QLineEdit()
        self.path_display.setReadOnly(True)
        self.path_display.setPlaceholderText("No folder selected")
        self.path_display.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(open_btn)
        toolbar.addWidget(self.path_display)

        if main_window:
            theme_btn = QPushButton(main_window.theme.toggle_label())
            theme_btn.setFixedWidth(32)
            theme_btn.clicked.connect(self._toggle_theme)
            self._theme_btn = theme_btn
            toolbar.addWidget(theme_btn)

        root_layout.addWidget(toolbar)

        # Scroll area with grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setContentsMargins(16, 16, 16, 16)
        scroll.setWidget(self.grid_widget)

        root_layout.addWidget(scroll)

        # Status bar
        self.status_label = QLabel("No folder selected")
        self.status_label.setContentsMargins(8, 2, 8, 2)
        self.status_label.setStyleSheet("font-size: 11px;")
        root_layout.addWidget(self.status_label)

    def closeEvent(self, event):
        for loader in self._loaders:
            loader.thumbnail_ready.disconnect()
            loader.quit()
            loader.wait()
        self._loaders.clear()
        super().closeEvent(event)

    def _toggle_theme(self):
        if self.main_window:
            self.main_window.theme.toggle()
            self._theme_btn.setText(self.main_window.theme.toggle_label())

    def _open_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Comics Folder")
        if folder:
            self.load_folder(folder)

    def scan_folder(self, folder_path: str) -> list[str]:
        result = []
        for f in sorted(os.listdir(folder_path)):
            if f.lower().endswith(".cbr"):
                result.append(os.path.join(folder_path, f))
        return result

    def load_folder(self, folder_path: str):
        # Stop and clear previous loaders
        for loader in self._loaders:
            loader.quit()
            loader.wait()
        self._loaders.clear()

        # Clear grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._cbr_files = self.scan_folder(folder_path)
        self.path_display.setText(folder_path)
        self.status_label.setText(f"{len(self._cbr_files)} comics found")

        cols = 6
        for i, cbr_path in enumerate(self._cbr_files):
            widget = ThumbnailWidget(cbr_path, self.main_window, self.grid_widget)
            row, col = divmod(i, cols)
            self.grid_layout.addWidget(widget, row, col)

            loader = ThumbnailLoader(cbr_path)
            loader.thumbnail_ready.connect(
                lambda pixmap, w=widget: w.image_label.setPixmap(pixmap)
            )
            loader.start()
            self._loaders.append(loader)
