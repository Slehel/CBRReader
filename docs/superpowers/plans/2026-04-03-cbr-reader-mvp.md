# CBR Reader MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Windows desktop comic book reader for .cbr files with a thumbnail library and single-page reader, using Python + PyQt6.

**Architecture:** A single `QMainWindow` uses a `QStackedWidget` to switch between `LibraryView` (thumbnail grid) and `ReaderView` (page display). CBR files are extracted to a temp directory on open via `rarfile`, and pages are displayed as scaled `QPixmap` images.

**Tech Stack:** Python 3.10+, PyQt6, Pillow, rarfile, pytest, pytest-qt

---

## File Structure

```
CBRReader/
├── main.py                        # Entry point: QApplication + MainWindow
├── requirements.txt               # All dependencies
├── src/
│   ├── __init__.py
│   ├── main_window.py             # MainWindow — owns QStackedWidget, theme state
│   ├── library_view.py            # LibraryView — folder picker + thumbnail grid
│   ├── reader_view.py             # ReaderView — page image + navigation toolbar
│   ├── cbr_extractor.py           # CBR extraction: extract pages, get cover, cleanup
│   ├── thumbnail_loader.py        # QThread worker: loads cover images in background
│   └── theme.py                   # DARK/LIGHT stylesheet strings + ThemeManager
└── tests/
    ├── conftest.py                # pytest-qt fixtures
    ├── test_cbr_extractor.py      # Unit tests for extraction logic
    ├── test_library_view.py       # Widget tests for LibraryView
    └── test_reader_view.py        # Widget tests for ReaderView
```

---

## Task 1: Project Setup & Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `main.py`
- Create: `src/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Create requirements.txt**

```
PyQt6>=6.6.0
Pillow>=10.0.0
rarfile>=4.1
pytest>=7.4.0
pytest-qt>=4.2.0
```

- [ ] **Step 2: Install dependencies**

Run in Windows PowerShell from `C:\Users\Lehel\ClaudeWorkSpace\CBRReader\`:
```powershell
pip install -r requirements.txt
```
Expected: All packages install without errors.

- [ ] **Step 3: Verify unrar is accessible**

```powershell
where unrar
```
Expected: Path to `unrar.exe` inside WinRAR folder (e.g. `C:\Program Files\WinRAR\UnRAR.exe`).  
If not found, add WinRAR's folder to PATH: `setx PATH "%PATH%;C:\Program Files\WinRAR"` then restart PowerShell.

- [ ] **Step 4: Create src/__init__.py**

Empty file — makes `src` a Python package.

```python
```

- [ ] **Step 5: Create tests/conftest.py**

```python
import pytest
from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app
```

- [ ] **Step 6: Create main.py shell**

```python
import sys
from PyQt6.QtWidgets import QApplication
from src.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

- [ ] **Step 7: Verify the shell runs**

```powershell
python main.py
```
Expected: A blank window opens and closes cleanly.

- [ ] **Step 8: Commit**

```powershell
git init
git add .
git commit -m "feat: project setup and dependency config"
```

---

## Task 2: CBR Extraction Engine

**Files:**
- Create: `src/cbr_extractor.py`
- Create: `tests/test_cbr_extractor.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_cbr_extractor.py
import os
import tempfile
import zipfile
import pytest
from PIL import Image
from src.cbr_extractor import extract_cbr, get_cover_path, cleanup


def make_fake_cbr(path: str, num_pages: int = 3) -> str:
    """Creates a fake .cbr (actually a zip) with PNG pages for testing."""
    cbr_path = os.path.join(path, "test.cbr")
    with zipfile.ZipFile(cbr_path, "w") as zf:
        for i in range(num_pages):
            img = Image.new("RGB", (100, 150), color=(i * 80, 100, 200))
            img_path = os.path.join(path, f"page_{i:03d}.png")
            img.save(img_path)
            zf.write(img_path, f"page_{i:03d}.png")
    return cbr_path


def test_extract_cbr_returns_sorted_image_paths(tmp_path):
    cbr = make_fake_cbr(str(tmp_path))
    pages = extract_cbr(str(cbr))
    assert len(pages) == 3
    assert all(p.endswith(".png") for p in pages)
    assert pages == sorted(pages)


def test_extract_cbr_files_exist_on_disk(tmp_path):
    cbr = make_fake_cbr(str(tmp_path))
    pages = extract_cbr(str(cbr))
    for p in pages:
        assert os.path.isfile(p)


def test_get_cover_path_returns_first_page(tmp_path):
    cbr = make_fake_cbr(str(tmp_path))
    cover = get_cover_path(str(cbr))
    assert cover is not None
    assert os.path.isfile(cover)


def test_cleanup_removes_temp_dir(tmp_path):
    cbr = make_fake_cbr(str(tmp_path))
    pages = extract_cbr(str(cbr))
    temp_dir = os.path.dirname(pages[0])
    cleanup(temp_dir)
    assert not os.path.exists(temp_dir)
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
pytest tests/test_cbr_extractor.py -v
```
Expected: `ImportError: cannot import name 'extract_cbr' from 'src.cbr_extractor'`

- [ ] **Step 3: Implement src/cbr_extractor.py**

```python
import os
import tempfile
import shutil
import zipfile
import rarfile

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}


def _is_image(filename: str) -> bool:
    return os.path.splitext(filename.lower())[1] in IMAGE_EXTENSIONS


def extract_cbr(cbr_path: str) -> list[str]:
    """Extract all pages from a CBR file to a temp dir. Returns sorted image paths."""
    temp_dir = tempfile.mkdtemp(prefix="cbr_")
    try:
        if zipfile.is_zipfile(cbr_path):
            with zipfile.ZipFile(cbr_path, "r") as zf:
                zf.extractall(temp_dir)
        else:
            with rarfile.RarFile(cbr_path, "r") as rf:
                rf.extractall(temp_dir)
    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise RuntimeError(f"Failed to extract {cbr_path}: {e}") from e

    pages = []
    for root, _, files in os.walk(temp_dir):
        for f in files:
            if _is_image(f):
                pages.append(os.path.join(root, f))

    return sorted(pages)


def get_cover_path(cbr_path: str) -> str | None:
    """Extract only the first page of a CBR and return its path."""
    pages = extract_cbr(cbr_path)
    if not pages:
        return None
    # Keep only the cover, remove everything else
    cover = pages[0]
    for p in pages[1:]:
        try:
            os.remove(p)
        except OSError:
            pass
    return cover


def cleanup(temp_dir: str) -> None:
    """Remove a temp directory created by extract_cbr."""
    shutil.rmtree(temp_dir, ignore_errors=True)
```

- [ ] **Step 4: Run tests to verify they pass**

```powershell
pytest tests/test_cbr_extractor.py -v
```
Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```powershell
git add src/cbr_extractor.py tests/test_cbr_extractor.py
git commit -m "feat: CBR extraction engine with tests"
```

---

## Task 3: Theme System

**Files:**
- Create: `src/theme.py`

- [ ] **Step 1: Create src/theme.py**

```python
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
        QApplication.instance().setStyleSheet(DARK if self._dark else LIGHT)

    def apply(self) -> None:
        QApplication.instance().setStyleSheet(DARK if self._dark else LIGHT)

    def toggle_label(self) -> str:
        return "☀" if self._dark else "☾"
```

- [ ] **Step 2: Commit**

```powershell
git add src/theme.py
git commit -m "feat: dark/light theme stylesheets and ThemeManager"
```

---

## Task 4: MainWindow Shell

**Files:**
- Create: `src/main_window.py`
- Create: `tests/test_main_window.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_main_window.py
from src.main_window import MainWindow


def test_main_window_shows_library_view_on_start(qapp):
    window = MainWindow()
    assert window.stack.currentIndex() == 0  # LibraryView is index 0


def test_main_window_can_switch_to_reader(qapp, tmp_path):
    from PIL import Image
    import zipfile, os
    # make a tiny fake cbr
    cbr = str(tmp_path / "test.cbr")
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    img_path = str(tmp_path / "p001.png")
    img.save(img_path)
    with zipfile.ZipFile(cbr, "w") as zf:
        zf.write(img_path, "p001.png")

    window = MainWindow()
    window.show_reader(cbr)
    assert window.stack.currentIndex() == 1  # ReaderView is index 1


def test_main_window_can_go_back_to_library(qapp, tmp_path):
    from PIL import Image
    import zipfile
    cbr = str(tmp_path / "test.cbr")
    img = Image.new("RGB", (10, 10))
    img_path = str(tmp_path / "p001.png")
    img.save(img_path)
    with zipfile.ZipFile(cbr, "w") as zf:
        zf.write(img_path, "p001.png")

    window = MainWindow()
    window.show_reader(cbr)
    window.show_library()
    assert window.stack.currentIndex() == 0
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
pytest tests/test_main_window.py -v
```
Expected: ImportError on `MainWindow`.

- [ ] **Step 3: Implement src/main_window.py**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```powershell
pytest tests/test_main_window.py -v
```
Expected: All 3 tests PASS.

- [ ] **Step 5: Commit**

```powershell
git add src/main_window.py tests/test_main_window.py
git commit -m "feat: MainWindow with view switching"
```

---

## Task 5: LibraryView — Folder Picker & Grid Layout

**Files:**
- Create: `src/library_view.py`
- Create: `tests/test_library_view.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_library_view.py
import os
import zipfile
from PIL import Image
from src.library_view import LibraryView


def make_cbr(folder: str, name: str) -> str:
    cbr_path = os.path.join(folder, name)
    img = Image.new("RGB", (100, 150), color=(100, 100, 200))
    img_path = os.path.join(folder, "p.png")
    img.save(img_path)
    with zipfile.ZipFile(cbr_path, "w") as zf:
        zf.write(img_path, "p.png")
    return cbr_path


def test_scan_folder_finds_cbr_files(qapp, tmp_path):
    make_cbr(str(tmp_path), "comic1.cbr")
    make_cbr(str(tmp_path), "comic2.cbr")
    view = LibraryView(None)
    files = view.scan_folder(str(tmp_path))
    assert len(files) == 2
    assert all(f.endswith(".cbr") for f in files)


def test_scan_folder_ignores_non_cbr(qapp, tmp_path):
    make_cbr(str(tmp_path), "comic1.cbr")
    open(os.path.join(str(tmp_path), "readme.txt"), "w").close()
    view = LibraryView(None)
    files = view.scan_folder(str(tmp_path))
    assert len(files) == 1


def test_status_label_updates_after_scan(qapp, tmp_path):
    make_cbr(str(tmp_path), "comic1.cbr")
    make_cbr(str(tmp_path), "comic2.cbr")
    view = LibraryView(None)
    view.load_folder(str(tmp_path))
    assert "2" in view.status_label.text()
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
pytest tests/test_library_view.py -v
```
Expected: ImportError on `LibraryView`.

- [ ] **Step 3: Implement src/library_view.py**

```python
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolBar,
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
        open_btn = QPushButton("📂 Open Folder")
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
        # Clear previous
        for loader in self._loaders:
            loader.quit()
            loader.wait()
        self._loaders.clear()

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
```

- [ ] **Step 4: Run tests to verify they pass**

```powershell
pytest tests/test_library_view.py -v
```
Expected: All 3 tests PASS.

- [ ] **Step 5: Commit**

```powershell
git add src/library_view.py tests/test_library_view.py
git commit -m "feat: LibraryView with folder scan and thumbnail grid"
```

---

## Task 6: Thumbnail Loader (Background Thread)

**Files:**
- Create: `src/thumbnail_loader.py`

- [ ] **Step 1: Create src/thumbnail_loader.py**

```python
import os
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
from PIL import Image
from src.cbr_extractor import get_cover_path, cleanup

THUMB_W = 88
THUMB_H = 110


class ThumbnailLoader(QThread):
    thumbnail_ready = pyqtSignal(QPixmap)

    def __init__(self, cbr_path: str):
        super().__init__()
        self.cbr_path = cbr_path

    def run(self):
        try:
            cover = get_cover_path(self.cbr_path)
            if not cover:
                return
            temp_dir = os.path.dirname(cover)

            img = Image.open(cover)
            img.thumbnail((THUMB_W, THUMB_H), Image.LANCZOS)

            # Save resized thumb to temp and load as QPixmap
            thumb_path = os.path.join(temp_dir, "_thumb.png")
            img.save(thumb_path)
            pixmap = QPixmap(thumb_path)

            cleanup(temp_dir)

            if not pixmap.isNull():
                self.thumbnail_ready.emit(pixmap)
        except Exception:
            pass  # Silently skip broken archives
```

- [ ] **Step 2: Verify thumbnails load when running the app**

```powershell
python main.py
```
Open a folder with at least one .cbr file. Expected: thumbnails appear in the grid (may take a moment per comic).

- [ ] **Step 3: Commit**

```powershell
git add src/thumbnail_loader.py
git commit -m "feat: background thumbnail loader thread"
```

---

## Task 7: ReaderView — Page Display

**Files:**
- Create: `src/reader_view.py`
- Create: `tests/test_reader_view.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_reader_view.py
import os
import zipfile
from PIL import Image
from src.reader_view import ReaderView


def make_cbr(folder: str, num_pages: int = 5) -> str:
    cbr_path = os.path.join(folder, "comic.cbr")
    with zipfile.ZipFile(cbr_path, "w") as zf:
        for i in range(num_pages):
            img = Image.new("RGB", (200, 300), color=(i * 40, 100, 200))
            img_path = os.path.join(folder, f"p{i:03d}.png")
            img.save(img_path)
            zf.write(img_path, f"p{i:03d}.png")
    return cbr_path


def test_load_comic_sets_page_count(qapp, tmp_path):
    view = ReaderView(None)
    cbr = make_cbr(str(tmp_path), num_pages=5)
    view.load_comic(cbr)
    assert view.total_pages == 5


def test_initial_page_is_zero(qapp, tmp_path):
    view = ReaderView(None)
    cbr = make_cbr(str(tmp_path))
    view.load_comic(cbr)
    assert view.current_page == 0


def test_next_page_increments(qapp, tmp_path):
    view = ReaderView(None)
    cbr = make_cbr(str(tmp_path))
    view.load_comic(cbr)
    view.next_page()
    assert view.current_page == 1


def test_prev_page_decrements(qapp, tmp_path):
    view = ReaderView(None)
    cbr = make_cbr(str(tmp_path))
    view.load_comic(cbr)
    view.next_page()
    view.prev_page()
    assert view.current_page == 0


def test_next_page_does_not_go_past_end(qapp, tmp_path):
    view = ReaderView(None)
    cbr = make_cbr(str(tmp_path), num_pages=2)
    view.load_comic(cbr)
    view.next_page()
    view.next_page()  # should clamp
    assert view.current_page == 1


def test_prev_page_does_not_go_below_zero(qapp, tmp_path):
    view = ReaderView(None)
    cbr = make_cbr(str(tmp_path))
    view.load_comic(cbr)
    view.prev_page()  # should clamp
    assert view.current_page == 0
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
pytest tests/test_reader_view.py -v
```
Expected: ImportError on `ReaderView`.

- [ ] **Step 3: Implement src/reader_view.py**

```python
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
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.image_label.setStyleSheet("background-color: #111111;")
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
```

- [ ] **Step 4: Run tests to verify they pass**

```powershell
pytest tests/test_reader_view.py -v
```
Expected: All 6 tests PASS.

- [ ] **Step 5: Commit**

```powershell
git add src/reader_view.py tests/test_reader_view.py
git commit -m "feat: ReaderView with page display and navigation"
```

---

## Task 8: Exit Cleanup

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Connect cleanup to app exit**

Replace `main.py` with:

```python
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
```

- [ ] **Step 2: Commit**

```powershell
git add main.py
git commit -m "feat: cleanup temp files on app exit"
```

---

## Task 9: Full Run & Smoke Test

- [ ] **Step 1: Run all tests**

```powershell
pytest tests/ -v
```
Expected: All tests PASS, no warnings about temp files.

- [ ] **Step 2: Manual smoke test**

```powershell
python main.py
```

Walk through this checklist manually:
1. App opens showing empty library with "No folder selected"
2. Click "📂 Open Folder" → pick a folder with .cbr files
3. Cover thumbnails load in the grid (async, one by one)
4. Status bar shows correct count (e.g. "5 comics found")
5. Double-click a comic → reader opens on page 1
6. Press → (right arrow) → advances to page 2
7. Press ← (left arrow) → goes back to page 1
8. Click "Next ▶" → advances; click "◀ Prev" → goes back
9. Page counter shows "X / N" correctly
10. Progress bar updates as you read
11. Click "← Library" → returns to library, temp files cleaned up
12. Click ☀ / ☾ → theme toggles between dark and light
13. Resize window → page scales correctly
14. Close app → no leftover temp folders in %TEMP%

- [ ] **Step 3: Final commit**

```powershell
git add .
git commit -m "feat: CBR Reader MVP complete"
```

---

## v2 Reference (do not implement now)

These are tracked in `docs/tasks.md` under v2:
- Reading progress memory per comic (JSON file, last page per path)
- CBZ support
- Zoom in/out
- Fullscreen mode
- Electron version
