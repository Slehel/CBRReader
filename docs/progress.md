# CBR Reader — Implementation Progress

**Last updated:** 2026-04-03  
**Completed:** Tasks 1–3 of 9  
**Status:** In progress

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

## Up Next

| Task | What it builds |
|---|---|
| **Task 4** | `MainWindow` — QStackedWidget that switches between LibraryView and ReaderView |
| Task 5 | `LibraryView` — folder picker + CBR thumbnail grid |
| Task 6 | `ThumbnailLoader` — background thread that loads cover images |
| Task 7 | `ReaderView` — single page display + navigation |
| Task 8 | Exit cleanup hook wired into app shutdown |
| Task 9 | Full test run + manual smoke test |
