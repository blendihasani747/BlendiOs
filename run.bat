@echo off
REM Quick launcher for BlendiOS desktop UI on Windows

cd /d "%~dp0"

if not exist ".venv" (
    echo Virtual environment not found. Run scripts\setup_dev_windows.bat first.
    exit /b 1
)

call .venv\Scripts\activate.bat
python -m blendios
