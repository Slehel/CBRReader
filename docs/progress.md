# CBR Reader — Implementation Progress

**Last updated:** 2026-04-03  
**Completed:** Tasks 1–9 of 9  
**Status:** MVP complete — pending manual smoke test on Windows

---

## Task 1 — Project Setup & Dependencies
**Commits:** `72b378a`, `1b1552c`

### What was built
- **`requirements.txt`** — lists all dependencies: PyQt6, Pillow, rarfile, pytest, pytest-qt
- **`src/__init__.py`** — empty file that makes `src` a proper Python package
- **`tests/conftest.py`** — sets up a session-scoped `qapp` fixture for PyQt6 tests
- **`main.py`** — app entry point: creates the window, connects a cleanup hook on exit
- **`.gitignore`** — ignores `__pycache__`, `.pytest_cache`, `.venv`, `.superpowers/` etc.
- Git repo initialized and connected to **https://github.com/Slehel/CBRReader**

### What was fixed during review
- Added a defensive `getattr` guard in `main.py` so the exit cleanup hook doesn't crash before `MainWindow` is fully built
- Added `.gitignore` (flagged as missing by code reviewer)

### Result
Skeleton is ready. Nothing visual runs yet — just the project structure, dependencies installed, and git wired up.

---

## Task 2 — CBR Extraction Engine
**Commits:** `6458509`, `29ad23d`

### What was built
- **`src/cbr_extractor.py`** — core extraction logic with 3 public functions:
  - `extract_cbr(cbr_path) -> list[str]` — extracts all pages from a `.cbr` or `.cbz` file into a temp directory, returns sorted image paths
  - `get_cover_path(cbr_path) -> tuple[str, str] | None` — extracts only the first page (cover), deletes the rest, returns `(cover_path, temp_dir)` so the caller can clean up
  - `cleanup(temp_dir)` — deletes the temp directory when done
- **`tests/test_cbr_extractor.py`** — 4 tests: sorted paths, files exist on disk, cover extraction, cleanup

### What was fixed during review
- Removed a hard-coded WSL path (`/mnt/c/Program Files/WinRAR/UnRAR.exe`) — replaced with `os.environ.get("UNRAR_TOOL")` so each environment configures its own unrar location
- Fixed `get_cover_path` to return `(cover_path, temp_dir)` tuple instead of just the path — callers need the temp_dir to clean up after themselves
- Changed `sorted(pages)` to `sorted(pages, key=lambda p: os.path.basename(p))` — more robust sorting when archives have subdirectories
- Removed unused `import tempfile` from tests

### Notes
- CBR files are RAR archives; CBZ files are ZIP archives — both are handled
- Tests use fake ZIP-based CBRs so they work in WSL without a Windows unrar binary
- On Windows with WinRAR installed, real `.cbr` files will extract automatically via PATH

### Result
The extraction engine is complete and tested. Any other module can call `extract_cbr()` to get all pages, or `get_cover_path()` to get just the cover thumbnail.

---

## Task 3 — Theme System
**Commits:** `c44fccc`, `dd8081b`

### What was built
- **`src/theme.py`** — dark/light theming with:
  - `DARK` — QSS stylesheet string (near-black background, light text)
  - `LIGHT` — QSS stylesheet string (light grey background, dark text)
  - `ThemeManager` class:
    - Defaults to **dark mode**
    - `toggle()` — flips between dark and light, applies immediately to the whole app
    - `apply()` — applies current theme (called once at startup)
    - `toggle_label()` — returns `☀` when dark (button label: "switch to light"), `☾` when light
    - `is_dark` — read-only property
- **`tests/test_theme.py`** — 6 tests: default state, toggle logic, label icons, no crash with QApplication

### What was fixed during review
- Added null guard: both `toggle()` and `apply()` now check `QApplication.instance() is not None` before applying the stylesheet — prevents crashes in isolated unit tests
- Added `tests/test_theme.py` (initially missed — the ThemeManager logic is testable even if the stylesheets aren't)

### Result
Theme system is complete. `MainWindow` will create a `ThemeManager` on startup and call `apply()`. Both the library and reader views will have a toggle button that calls `toggle()`.

---

---

## Task 4 — MainWindow Shell
**Commit:** `61eadbc`

### What was built
- **`src/main_window.py`** — `QMainWindow` with a `QStackedWidget` as central widget:
  - Index 0 → `LibraryView`
  - Index 1 → `ReaderView`
  - `show_library()` — calls `reader_view.cleanup()` then switches to index 0
  - `show_reader(cbr_path)` — calls `reader_view.load_comic(cbr_path)` then switches to index 1
  - Creates and applies `ThemeManager` on startup
- **`src/library_view.py`** — minimal stub `QWidget` (full implementation in Task 5)
- **`src/reader_view.py`** — stub `QWidget` with `load_comic` / `cleanup` (full implementation in Task 7)
- **`tests/test_main_window.py`** — 3 tests: initial index, switch to reader, switch back to library

### Result
The app shell is wired. `main.py` can create a `MainWindow`, show it, and the exit hook (`reader_view.cleanup()`) is already connected. View switching works end-to-end.

---

---

## Task 5 — LibraryView & Task 6 — ThumbnailLoader
**Commit:** `f27949e`

### What was built
- **`src/library_view.py`** — full implementation replacing stub:
  - Toolbar: "Open Folder" button, read-only path display, optional theme toggle
  - `scan_folder(path)` — returns sorted `.cbr` paths, ignores everything else
  - `load_folder(path)` — clears grid, scans folder, creates `ThumbnailWidget` per comic, starts one `ThumbnailLoader` thread per comic
  - `closeEvent` — disconnects signals and joins all threads before GC (prevents SIGABRT in Qt)
- **`src/thumbnail_loader.py`** — `QThread` that extracts cover via `get_cover_path`, resizes with Pillow, emits `QPixmap` via signal
- **`tests/test_library_view.py`** — 3 tests: scan finds CBRs, ignores non-CBR, status label updates

### What was fixed vs plan
- `get_cover_path` returns a tuple `(cover_path, temp_dir)` — plan's ThumbnailLoader treated it as a string; fixed to unpack correctly
- Added `closeEvent` with signal disconnect + thread join — without this, Qt raises SIGABRT when GC collects running QThread objects

### Result
Library view is fully functional. Opening a folder scans for CBRs, populates the grid, and loads thumbnails in the background.

---

## Task 7 — ReaderView
**Commit:** `f2129da`

### What was built
- **`src/reader_view.py`** — full implementation replacing stub:
  - Toolbar: "← Library" back button, Prev/Next buttons, page counter label, theme toggle
  - `load_comic(cbr_path)` — extracts all pages, sets `total_pages` and `current_page = 0`
  - `next_page()` / `prev_page()` — clamped navigation, re-renders image
  - `_show_current_page()` — scales pixmap to fit widget, updates page label and progress bar
  - `keyPressEvent` — arrow keys and space bar for navigation
  - `resizeEvent` — re-renders current page when window is resized
  - `cleanup()` — deletes temp dir and resets state
- **`tests/test_reader_view.py`** — 6 tests: page count, initial page, next/prev, clamp at both ends

### Result
Reader is fully functional. Pages display scaled to the window, keyboard navigation works, and temp files are cleaned up on exit.

---

## Task 8 — Exit Cleanup
**No new commit needed** — already implemented in Task 1 review.

`main.py` already has a `getattr`-guarded `on_exit` hook connected to `app.aboutToQuit` that calls `reader_view.cleanup()`.

---

## Task 9 — Full Test Run
**22/22 tests passing** — no warnings.

---

## Manual Smoke Test (for user to run on Windows)

```powershell
python main.py
```

Checklist:
1. App opens showing empty library with "No folder selected"
2. Click "Open Folder" → pick a folder with .cbr files
3. Cover thumbnails load in the grid (async, one by one)
4. Status bar shows correct count (e.g. "5 comics found")
5. Double-click a comic → switches to ReaderView
6. First page displays, "1 / N" shown in toolbar
7. Next/Prev buttons and arrow keys navigate pages
8. "← Library" returns to the grid
9. Close the app — no temp files left in `%TEMP%`

---

## Status: MVP Complete
