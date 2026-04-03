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
