# CBR Reader — Project Context

## Stack
- Python 3.10+, PyQt6, Pillow, rarfile, pytest, pytest-qt
- Entry point: `main.py` → creates `QApplication` + `MainWindow`, connects `reader_view.cleanup()` to `aboutToQuit`

## Architecture
```
MainWindow (QMainWindow)
└── QStackedWidget
    ├── index 0 → LibraryView   (folder picker + thumbnail grid)
    └── index 1 → ReaderView    (single page display + navigation)
```
- `MainWindow.show_library()` — calls `reader_view.cleanup()` then switches to index 0
- `MainWindow.show_reader(cbr_path)` — calls `reader_view.load_comic(cbr_path)` then switches to index 1

## Key rules per module

**`src/cbr_extractor.py`**
- `extract_cbr(path)` → `list[str]` sorted by basename
- `get_cover_path(path)` → `tuple[str, str] | None` — returns `(cover_path, temp_dir)`, caller must call `cleanup(temp_dir)`
- Temp dirs use prefix `cbr_`
- WinRAR auto-detected at `C:\Program Files\WinRAR\UnRAR.exe` and `Program Files (x86)` before falling back to `UNRAR_TOOL` env var

**`src/thumbnail_loader.py`**
- `QThread` subclass — emits `thumbnail_ready(QPixmap)` signal when done
- Always `disconnect()` the signal before `quit()` + `wait()` in cleanup — otherwise queued signal fires on deleted widget → crash

**`src/library_view.py`**
- `closeEvent` must disconnect all loader signals and join threads before `super().closeEvent()` — prevents SIGABRT when Qt GCs running QThread objects
- `load_folder()` stops previous loaders before starting new ones

**`src/reader_view.py`**
- `image_label` has `objectName = "reader_canvas"` — background is controlled by theme QSS, not inline style
- `cleanup()` deletes the temp dir and resets page state

**`src/theme.py`**
- `DARK` / `LIGHT` are QSS strings applied app-wide via `QApplication.setStyleSheet()`
- `QLabel#reader_canvas` rule in both themes controls the reader background
- Font stack: `"Segoe UI", "SF Pro Display", "Helvetica Neue", Arial, sans-serif`

## Tests
- Fake CBRs use `zipfile` (not rarfile) so tests work without WinRAR
- `tests/conftest.py` provides a session-scoped `qapp` fixture
- After any test that calls `load_folder()`, call `view.close()` to join threads before GC

## Workflow
- Feature work goes on a `feature/` branch
- When done: open a PR to `master`
- `ComicReaderV1` branch = snapshot of the working MVP

## User preference
- Always explain what was built and why after completing each task — the user learns from these explanations
