@echo off
REM Canon System Startup Script for Windows
REM Starts both backend and frontend servers

echo Starting Canon System...

REM Create data directories if they don't exist
if not exist "data\characters" mkdir data\characters
if not exist "data\environments" mkdir data\environments
if not exist "data\templates" mkdir data\templates

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python 3 is required but not installed.
    exit /b 1
)

REM Check if Node is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js is required but not installed.
    exit /b 1
)

REM Start backend
echo Starting backend server...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install dependencies
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

REM Start backend in background
start "Canon Backend" cmd /k "venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000"
cd ..

REM Wait for backend to start
timeout /t 3 /nobreak >nul

echo Backend running on http://localhost:8000

REM Start frontend
echo Starting frontend server...
cd frontend

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

REM Start frontend
start "Canon Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ===============================================
echo   Canon System is running!
echo ===============================================
echo.
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo   Close the terminal windows to stop servers
echo ===============================================
