# CBR Reader — Design Document

**Date:** 2026-04-03  
**Version:** 1.0 (MVP)  
**Tech stack:** Python + PyQt6  
**Platform:** Windows desktop  

---

## Goal

A free, uninterrupted comic book reader for `.cbr` files.  
Replaces IceCream Ebook Reader 6 (which paywalls after a few pages).

---

## MVP Scope (v1)

| Feature | Included |
|---|---|
| Open a folder and show CBR covers as thumbnails | ✅ |
| Double-click a comic to open the reader | ✅ |
| Single-page display, scaled to fit window | ✅ |
| Navigate pages with arrow keys and Prev/Next buttons | ✅ |
| Dark / Light theme toggle | ✅ |
| Back button returns to library | ✅ |
| Reading progress memory per comic | ❌ v2 |

---

## Architecture

The app has two views managed by a single `QMainWindow`:

```
MainWindow
├── LibraryView     — thumbnail grid of all .cbr files in chosen folder
└── ReaderView      — single-page image viewer for the open comic
```

CBR files are RAR archives. We extract pages into a temp folder on open, display them as images.

**Key libraries:**
- `PyQt6` — GUI framework
- `Pillow` — image loading and thumbnail generation
- `rarfile` — CBR/RAR extraction (pure Python, requires `unrar.exe` on Windows)

**System requirement:**  
`unrar.exe` from WinRAR must be on the system PATH. User already has WinRAR installed — no additional setup needed.

---

## UI Screens

### Library View
- Toolbar: "Open Folder" button, current folder path, theme toggle
- Grid of cover thumbnails (first page of each CBR)
- Comic filename shown below each thumbnail
- Double-click → opens ReaderView
- Status bar: "N comics found"

### Reader View
- Toolbar: "← Library" back button, Prev/Next buttons, "Page X / N" counter, theme toggle
- Main area: current page image, centered, scaled to fit window
- Progress bar at bottom
- Keyboard: Left/Right arrows to navigate

---

## v2 Features (after MVP)

- Reading progress: remember last page per comic
- Electron/web version of the app
- CBZ support (ZIP-based comic archives)
- Zoom in/out on pages
- Fullscreen mode

---
