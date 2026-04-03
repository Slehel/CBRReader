# CBR Reader Packaging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce `dist/CBRReader/CBRReader.exe` with a custom icon and a desktop shortcut, by running a single `build.bat` from Windows cmd.

**Architecture:** A self-contained `build.bat` at the project root installs PyInstaller if missing, runs a onedir build with the correct flags, then creates a `.lnk` desktop shortcut via PowerShell. No application code changes needed.

**Tech Stack:** PyInstaller 6+, PyQt6, Python 3.10+, Windows PowerShell (for shortcut creation)

---

### Task 1: Create `build.bat`

**Files:**
- Create: `build.bat`

> Note: This is a build script, not application logic — TDD does not apply. Verification is done by running the script and confirming the output.

- [ ] **Step 1: Create `build.bat` at the project root**

```bat
@echo off
setlocal EnableDelayedExpansion

set "PROJECT_DIR=%~dp0"
:: Remove trailing backslash
if "%PROJECT_DIR:~-1%"=="\" set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

set "DIST_DIR=%PROJECT_DIR%\dist\CBRReader"
set "EXE=%DIST_DIR%\CBRReader.exe"

echo ============================================
echo  CBR Reader - Build Script
echo ============================================

echo.
echo [1/3] Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo   Installing PyInstaller...
    pip install pyinstaller
) else (
    echo   PyInstaller already installed.
)

echo.
echo [2/3] Building CBRReader.exe (onedir)...
cd /d "%PROJECT_DIR%"
pyinstaller ^
    --onedir ^
    --windowed ^
    --icon=icon.ico ^
    --name=CBRReader ^
    --hidden-import=PyQt6.sip ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=rarfile ^
    --noconfirm ^
    main.py

if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed. See output above.
    pause
    exit /b 1
)

echo.
echo [3/3] Creating desktop shortcut...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$ws = New-Object -ComObject WScript.Shell; " ^
    "$desktop = [Environment]::GetFolderPath('Desktop'); " ^
    "$s = $ws.CreateShortcut($desktop + '\CBR Reader.lnk'); " ^
    "$s.TargetPath = '%EXE:\=\\%'; " ^
    "$s.IconLocation = '%EXE:\=\\%,0'; " ^
    "$s.WorkingDirectory = '%DIST_DIR:\=\\%'; " ^
    "$s.Save()"

if errorlevel 1 (
    echo.
    echo WARNING: Shortcut creation failed. You can create it manually:
    echo   Target:    %EXE%
    echo   Start in:  %DIST_DIR%
) else (
    echo   Shortcut created: %USERPROFILE%\Desktop\CBR Reader.lnk
)

echo.
echo ============================================
echo  Done! Launch: %EXE%
echo ============================================
pause
```

- [ ] **Step 2: Commit**

```bash
git add build.bat
git commit -m "feat: add build.bat for PyInstaller onedir packaging with desktop shortcut"
```

---

### Task 2: Run the build and verify

> Run this from a **Windows cmd or PowerShell** window, not WSL. Navigate to the project folder first.

- [ ] **Step 1: Open Windows cmd and navigate to the project**

```cmd
cd C:\Users\Lehel\ClaudeWorkSpace\CBRReader
```

- [ ] **Step 2: Run the build script**

```cmd
build.bat
```

Expected output (abridged):
```
[1/3] Checking PyInstaller...
  PyInstaller already installed.  (or: Installing PyInstaller...)

[2/3] Building CBRReader.exe (onedir)...
...
Building EXE from EXE-00.toc
Appending PKG archive to custom ELF section in EXE
Building EXE from EXE-00.toc completed successfully.
...

[3/3] Creating desktop shortcut...
  Shortcut created: C:\Users\Lehel\Desktop\CBR Reader.lnk

Done! Launch: C:\Users\Lehel\ClaudeWorkSpace\CBRReader\dist\CBRReader\CBRReader.exe
```

- [ ] **Step 3: Verify the exe launches correctly**

Double-click `dist\CBRReader\CBRReader.exe` (or the desktop shortcut).

Expected: CBR Reader opens with no console window, shows the library view, icon appears in the taskbar and title bar.

- [ ] **Step 4: Verify the icon appears on the desktop shortcut**

Check `%USERPROFILE%\Desktop` — `CBR Reader.lnk` should show the orange/blue comic book icon.

---

### Task 3: Troubleshooting (if build fails)

> Only needed if Task 2 fails. Skip otherwise.

- [ ] **If PyQt6 import errors at runtime:** Add `--collect-all PyQt6` to the `pyinstaller` command in `build.bat` (replaces the individual `--hidden-import` flags):

```bat
pyinstaller ^
    --onedir ^
    --windowed ^
    --icon=icon.ico ^
    --name=CBRReader ^
    --collect-all PyQt6 ^
    --hidden-import=rarfile ^
    --noconfirm ^
    main.py
```

Then re-run `build.bat`.

- [ ] **If the app opens but can't read CBR files:** This is expected if WinRAR is not installed. The app relies on `C:\Program Files\WinRAR\UnRAR.exe` being present on the machine — same as when running from source.

- [ ] **If the shortcut icon doesn't update immediately:** Right-click the shortcut → Properties → Change Icon → browse to `dist\CBRReader\CBRReader.exe` → OK. Windows icon cache sometimes lags.

---

### Task 4: Final commit

- [ ] **Step 1: Commit build artifacts note to .gitignore**

Add the following to `.gitignore` (if not already present):

```
dist/
build/
*.spec
__pycache__/
.superpowers/
```

```bash
git add .gitignore
git commit -m "chore: ignore PyInstaller output dirs and brainstorm session files"
```
