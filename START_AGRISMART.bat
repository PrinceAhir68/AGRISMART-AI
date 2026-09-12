@echo off
title AgriSmart AI - Intelligent Agricultural Decision Platform
color 0A
cls
echo =====================================================================
echo               * WELCOME TO AGRISMART AI SYSTEM *
echo         Autonomous Agricultural Intelligence & Pathology Platform
echo =====================================================================
echo.

:: 1. Check Python installation
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your system PATH!
    echo.
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    echo NOTE: Make sure to check the box: "Add python.exe to PATH" during installation.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VER=%%i
echo [OK] Found %PYTHON_VER%

:: 2. Check and install dependencies
echo.
echo [2/4] Verifying required Python packages...
python -c "import fastapi, uvicorn, torch, torchvision, PIL, numpy, httpx" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Required packages not yet installed. Installing dependencies...
    echo This may take 1-2 minutes on first run. Please wait...
    echo.
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Dependency installation encountered an issue.
        pause
        exit /b 1
    )
) else (
    echo [OK] All core dependencies verified!
)

:: 3. Initialize / verify SQLite database
echo.
echo [3/4] Initializing local database (agrismart.db)...
python -c "from app.database import init_database; init_database(); print('[OK] Database ready.')"

:: 4. Free Port 8000 if lingering & Start Server
echo.
echo [4/4] Preparing port 8000 and starting AgriSmart AI Server...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo =====================================================================
echo   Web Application URL: http://127.0.0.1:8000
echo   Local Network:       http://localhost:8000
echo =====================================================================
echo.
echo Launching your web browser in 2 seconds...
start "" "http://127.0.0.1:8000"
echo Server is running! (Press Ctrl+C to stop)
echo.
python app/main.py
pause
