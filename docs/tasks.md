# CBR Reader — Task Plan

**Legend:**  
🔴 Priority 1 — Must have (MVP blocker)  
🟡 Priority 2 — Should have (MVP complete)  
🟢 Priority 3 — Nice to have (v2)

---

## Implementation Order

Tasks are listed in the order they will be worked on. Each task builds on the previous.

---

### Phase 1 — Project Setup

| # | Task | Priority | Notes |
|---|---|---|---|
| 1 | Set up Python project structure | 🔴 | Create folders, `main.py`, `requirements.txt` |
| 2 | Install and verify dependencies | 🔴 | PyQt6, Pillow, patool/rarfile |
| 3 | Create `MainWindow` shell | 🔴 | Bare window that launches and closes cleanly |

---

### Phase 2 — CBR Extraction

| # | Task | Priority | Notes |
|---|---|---|---|
| 4 | Implement CBR file extraction | 🔴 | Extract RAR → temp folder, return sorted list of image paths |
| 5 | Extract cover (first page) for thumbnails | 🔴 | Used by library view; extract only page 1 for speed |
| 6 | Handle extraction errors gracefully | 🟡 | Bad file, missing unrar tool, corrupted archive |

---

### Phase 3 — Library View

| # | Task | Priority | Notes |
|---|---|---|---|
| 7 | Build `LibraryView` widget with thumbnail grid | 🔴 | QScrollArea + grid layout of cover images |
| 8 | "Open Folder" button + folder picker dialog | 🔴 | QFileDialog, scan for `.cbr` files |
| 9 | Load and display cover thumbnails | 🔴 | Async/threaded so UI doesn't freeze on large folders |
| 10 | Show filename below each thumbnail | 🟡 | Truncate long names with ellipsis |
| 11 | Double-click thumbnail → open reader | 🔴 | Switch MainWindow to ReaderView |
| 12 | Status bar showing comic count | 🟡 | "N comics found" |

---

### Phase 4 — Reader View

| # | Task | Priority | Notes |
|---|---|---|---|
| 13 | Build `ReaderView` widget | 🔴 | QLabel or QGraphicsView for image display |
| 14 | Load and display pages scaled to window | 🔴 | Fit-to-window scaling with aspect ratio preserved |
| 15 | Prev / Next buttons | 🔴 | Toolbar buttons |
| 16 | Left / Right arrow key navigation | 🔴 | Override `keyPressEvent` |
| 17 | "Page X / N" counter display | 🟡 | Updates on every page change |
| 18 | Progress bar at bottom | 🟡 | Proportional to current page / total pages |
| 19 | "← Library" back button | 🔴 | Switch back to LibraryView, clean up temp files |

---

### Phase 5 — Theming

| # | Task | Priority | Notes |
|---|---|---|---|
| 20 | Dark theme stylesheet | 🟡 | Default theme |
| 21 | Light theme stylesheet | 🟡 | |
| 22 | Theme toggle button | 🟡 | ☀/☾ icon in toolbar, applies to whole app |

---

### Phase 6 — Polish & Packaging

| # | Task | Priority | Notes |
|---|---|---|---|
| 23 | Window resize → rescale current page | 🟡 | Re-fit image when window is resized |
| 24 | Clean up temp folder on exit | 🔴 | Don't leave extracted files behind |
| 25 | App icon | 🟢 | |
| 26 | Package as `.exe` with PyInstaller | 🟢 | Single-file Windows executable, no Python needed |

---

### v2 — Future Tasks

| # | Task | Priority | Notes |
|---|---|---|---|
| 27 | Save/load reading progress per comic | 🟢 | JSON file tracking last page per CBR |
| 28 | CBZ (ZIP) support | 🟢 | |
| 29 | Zoom in/out on pages | 🟢 | |
| 30 | Fullscreen mode | 🟢 | |
| 31 | Electron version | 🟢 | Separate project |

---

## Start Order Summary

```
1 → 2 → 3        (project skeleton)
       ↓
4 → 5 → 6        (CBR extraction engine)
       ↓
7 → 8 → 9 → 10 → 11 → 12    (library view)
                      ↓
         13 → 14 → 15 → 16 → 17 → 18 → 19    (reader view)
                                        ↓
                              20 → 21 → 22    (theming)
                                        ↓
                              23 → 24 → 25 → 26    (polish + packaging)
```
