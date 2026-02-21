@echo off
REM ViT Deepfake Detector - Startup Script for Windows

echo.
echo ====================================
echo ViT Deepfake Detector - Startup
echo ====================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if dependencies are installed
pip show transformers > nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install --upgrade pip
    pip install -r requirements.txt
)

REM Check if database exists
if not exist backend\users.db (
    echo.
    echo Creating database...
    python backend\init_db.py
    echo.
)

REM Start the application
echo.
echo ====================================
echo Starting ViT Deepfake Detector
echo ====================================
echo.
echo Application running at: http://localhost:5000
echo.
echo Press CTRL+C to stop the server
echo.

python backend\app.py

pause
