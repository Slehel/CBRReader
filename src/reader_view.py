import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QToolBar, QPushButton,
    QLabel, QSizePolicy, QProgressBar
)
from PyQt6.QtGui import QPixmap, QKeyEvent
from PyQt6.QtCore import Qt
from src.cbr_extractor import extract_cbr, cleanup


class ReaderView(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self._pages: list[str] = []
        self._temp_dir: str | None = None
        self.current_page: int = 0
        self.total_pages: int = 0

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)

        self.back_btn = QPushButton("← Library")
        self.back_btn.clicked.connect(self._go_back)

        self.prev_btn = QPushButton("◀ Prev")
        self.prev_btn.clicked.connect(self.prev_page)

        self.page_label = QLabel("0 / 0")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setMinimumWidth(80)

        self.next_btn = QPushButton("Next ▶")
        self.next_btn.clicked.connect(self.next_page)

        spacer_left = QWidget()
        spacer_left.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        spacer_right = QWidget()
        spacer_right.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        toolbar.addWidget(self.back_btn)
        toolbar.addWidget(spacer_left)
        toolbar.addWidget(self.prev_btn)
        toolbar.addWidget(self.page_label)
        toolbar.addWidget(self.next_btn)
        toolbar.addWidget(spacer_right)

        if main_window:
            self._theme_btn = QPushButton(main_window.theme.toggle_label())
            self._theme_btn.setFixedWidth(32)
            self._theme_btn.clicked.connect(self._toggle_theme)
            toolbar.addWidget(self._theme_btn)

        root_layout.addWidget(toolbar)

        # Page image
        self.image_label = QLabel()
        self.image_label.setObjectName("reader_canvas")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root_layout.addWidget(self.image_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setRange(0, 100)
        root_layout.addWidget(self.progress_bar)

    def load_comic(self, cbr_path: str):
        self.cleanup()
        self._pages = extract_cbr(cbr_path)
        if self._pages:
            self._temp_dir = os.path.dirname(self._pages[0])
        self.total_pages = len(self._pages)
        self.current_page = 0
        self._show_current_page()

    def _show_current_page(self):
        if not self._pages:
            return
        path = self._pages[self.current_page]
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)

        self.page_label.setText(f"{self.current_page + 1} / {self.total_pages}")
        if self.total_pages > 1:
            pct = int(self.current_page / (self.total_pages - 1) * 100)
            self.progress_bar.setValue(pct)
        else:
            self.progress_bar.setValue(100)

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self._show_current_page()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._show_current_page()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Right, Qt.Key.Key_Space):
            self.next_page()
        elif event.key() == Qt.Key.Key_Left:
            self.prev_page()
        else:
            super().keyPressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._show_current_page()

    def cleanup(self):
        if self._temp_dir:
            cleanup(self._temp_dir)
            self._temp_dir = None
        self._pages = []
        self.total_pages = 0
        self.current_page = 0

    def _go_back(self):
        if self.main_window:
            self.main_window.show_library()

    def _toggle_theme(self):
        if self.main_window:
            self.main_window.theme.toggle()
            self._theme_btn.setText(self.main_window.theme.toggle_label())
            if hasattr(self.main_window, "library_view"):
                lv = self.main_window.library_view
                if hasattr(lv, "_theme_btn"):
                    lv._theme_btn.setText(self.main_window.theme.toggle_label())
