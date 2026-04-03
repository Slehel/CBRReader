# CBR Reader — Packaging & Desktop Shortcut Design

**Date:** 2026-04-03  
**Scope:** Package the CBR Reader PyQt6 app as a Windows desktop app using PyInstaller (onedir), with a desktop shortcut and custom icon.

---

## Goal

Produce a launchable Windows app from the existing Python/PyQt6 project so the user can start it from a desktop shortcut with a custom icon.

---

## Approach

PyInstaller **onedir** mode:
- Produces `dist/CBRReader/CBRReader.exe` + supporting DLLs/assets in one folder
- Fast launch (no extraction step)
- Desktop shortcut points to `dist\CBRReader\CBRReader.exe`

---

## Files to Create

### `build.bat`
Runs under Windows Python (double-click from Explorer or run in cmd). Does three things:
1. Installs PyInstaller if not present
2. Runs PyInstaller with the correct flags
3. Creates a desktop shortcut via PowerShell

PyInstaller flags:
- `--onedir` — folder dist
- `--windowed` — suppress console window
- `--icon=icon.ico` — custom icon
- `--name=CBRReader` — exe name
- `--hidden-import` entries for PyQt6 submodules that PyInstaller misses at analysis time

### `CBRReader.spec` (optional override)
If hidden imports need fine-tuning after first build, we edit the generated `.spec` file instead of the command line. Not pre-created — adjust after first build if needed.

---

## Desktop Shortcut

Created by a PowerShell one-liner embedded in `build.bat`:

```powershell
$ws = New-Object -ComObject WScript.Shell
$s  = $ws.CreateShortcut("$env:USERPROFILE\Desktop\CBR Reader.lnk")
$s.TargetPath   = "<abs path to dist\CBRReader\CBRReader.exe>"
$s.IconLocation = "<abs path to dist\CBRReader\CBRReader.exe>,0"
$s.WorkingDirectory = "<abs path to dist\CBRReader>"
$s.Save()
```

The shortcut pulls the icon from the embedded exe resource (set by `--icon`), so no separate `.ico` file is needed at runtime.

---

## Known Constraints

- **Must run from Windows Python**, not WSL — PyInstaller builds for the platform it runs on.
- **WinRAR / UnRAR:** `rarfile` auto-detects `C:\Program Files\WinRAR\UnRAR.exe` at runtime. No need to bundle it — the app will find it on the user's machine as before.
- **First build is slow** (~30-60s); subsequent rebuilds are faster due to PyInstaller caching.

---

## Out of Scope

- Code signing (not needed for personal use)
- NSIS installer
- Auto-update mechanism
