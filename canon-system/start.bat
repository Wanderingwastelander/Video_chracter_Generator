@echo off
REM Canon System Startup Script for Windows
REM Starts both backend and frontend servers

echo.
echo ============================================
echo        CANON SYSTEM LAUNCHER
echo ============================================
echo.

REM Create data directories if they don't exist
if not exist "data\characters" mkdir data\characters
if not exist "data\environments" mkdir data\environments
if not exist "data\templates" mkdir data\templates

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3 is required but not installed.
    echo Please download Python from: https://www.python.org/
    pause
    exit /b 1
)

REM Check if Node is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is required but not installed.
    echo Please download Node.js from: https://nodejs.org/
    pause
    exit /b 1
)

REM Get the full path to this script's directory
set SCRIPT_DIR=%~dp0

REM Start backend server in new window
echo [1/2] Starting Backend Server...
start "Canon Backend" cmd /k ""%SCRIPT_DIR%backend\start-backend.bat""

REM Wait a moment for backend to initialize
timeout /t 2 /nobreak >nul

REM Start frontend server in new window
echo [2/2] Starting Frontend Server...
start "Canon Frontend" cmd /k ""%SCRIPT_DIR%frontend\start-frontend.bat""

REM Wait a moment for frontend to initialize
timeout /t 2 /nobreak >nul

echo.
echo ============================================
echo   Canon System is starting!
echo ============================================
echo.
echo   Frontend:  http://localhost:5173
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo   Two terminal windows have been opened.
echo   Close them to stop the servers.
echo.
echo ============================================
echo.
echo Opening browser...
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo Press any key to close this launcher window...
echo (The servers will keep running)
pause >nul
