@echo off
REM BlendiOS — Windows Development Setup Script (Command Prompt)
REM Run this script from the project root directory.
REM Example: scripts\setup_dev_windows.bat

echo.
echo ===========================================
echo  BlendiOS Windows Development Setup
echo ===========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python was not found. Please install Python 3.11+ and add it to your PATH.
    exit /b 1
)

REM Create virtual environment
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip and install dependencies
echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing BlendiOS and dependencies...
pip install -e ".[dev]"

REM Configure environment file
if not exist ".env" (
    echo Creating .env from .env.example...
    copy .env.example .env

    for /f "delims=" %%i in ('python -c "import secrets; print(secrets.token_hex(32))"') do set SECRET_KEY=%%i
    powershell -Command "(Get-Content '.env') -replace 'BLENDIOS_SECRET_KEY=change-me-in-production', 'BLENDIOS_SECRET_KEY=%SECRET_KEY%' | Set-Content '.env'"
    echo Generated a random BLENDIOS_SECRET_KEY in .env
) else (
    echo .env already exists. Skipping.
)

REM Seed database
echo Initializing SQLite database...
python scripts\seed_db.py

echo.
echo ===========================================
echo  Setup complete!
echo ===========================================
echo.
echo Run BlendiOS desktop:
echo   .venv\Scripts\activate.bat
echo   python -m blendios
echo.
echo Run API server:
echo   uvicorn blendios.api.main:app --reload
echo.
echo Run Streamlit dashboard:
echo   streamlit run dashboards\streamlit_dashboard.py
echo.

pause
