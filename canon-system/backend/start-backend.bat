@echo off
echo Starting Canon Backend Server...

REM Get the directory where this script is located
cd /d "%~dp0"

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    echo Installing dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo.
echo Backend server starting on http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
