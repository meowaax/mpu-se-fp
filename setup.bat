@echo off
chcp 65001 >nul
title CRM Assistant - Setup and Run
color 0A

echo.
echo ============================================================
echo            🚀 CRM ASSISTANT - AUTOMATED SETUP
echo ============================================================
echo.

REM Check if Python is installed
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python 3.10 or higher:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
python --version
echo [OK] Python found!
echo.

REM Create virtual environment if it doesn't exist
echo [2/6] Setting up virtual environment...
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created!
) else (
    echo [OK] Virtual environment already exists!
)
echo.

REM Activate virtual environment
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated!
echo.

REM Install all required packages
echo [4/6] Installing required packages...
echo.
echo Installing core packages...
pip install --upgrade pip >nul 2>&1
pip install Flask==3.1.0
pip install python-dotenv==1.0.1
pip install requests==2.32.3
pip install pandas==2.2.3
pip install black==24.3.0

echo.
echo ✅ All packages installed successfully!
echo    - Flask 3.1.0
echo    - python-dotenv 1.0.1
echo    - requests 2.32.3
echo    - pandas 2.2.3
echo    - black 24.3.0 (code formatter)
echo.

REM Check database
echo [5/6] Checking database...
if not exist "db\crm.db" (
    echo [WARNING] Database not found!
    echo.
    echo Options:
    echo   1. Run migration (if CSV files exist)
    echo   2. Continue with empty database
    echo.
    choice /C 12 /N /M "Choose [1 or 2]: "
    if errorlevel 2 (
        echo [OK] Continuing with empty database...
    ) else (
        echo Running data migration...
        if exist "db\database.py" (
            python db\database.py
        ) else (
            echo [ERROR] Migration script not found!
        )
    )
) else (
    echo [OK] Database found!
)
echo.

REM Check .env file
echo [6/6] Checking configuration...
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo.
    echo Creating sample .env file...
    (
        echo # Qwen API Configuration
        echo QWEN_API_KEY=sk-your-api-key-here
        echo QWEN_MODEL=qwen-plus
        echo.
        echo # Database Configuration ^(optional^)
        echo # DATABASE_URL=sqlite:///db/crm.db
    ) > .env
    echo.
    echo [IMPORTANT] Please edit the .env file and add your Qwen API Key!
    echo    File location: %CD%\.env
    echo.
    start notepad .env
    echo.
    pause
) else (
    echo [OK] .env file found!
)
echo.

REM Start server
echo ============================================================
echo            🎯 STARTING CRM ASSISTANT SERVER
echo ============================================================
echo.
echo 🌐 Access the application at: http://127.0.0.1:8000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Wait 2 seconds then open browser
timeout /t 2 /nobreak >nul
start "" http://127.0.0.1:8000

REM Run the server
python server.py

REM If server stops
echo.
echo ============================================================
echo            👋 SERVER STOPPED
echo ============================================================
echo.
pause