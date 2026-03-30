@echo off
echo Starting Canon Frontend Server...

REM Get the directory where this script is located
cd /d "%~dp0"

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

echo.
echo Frontend server starting on http://localhost:5173
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the development server
npm run dev
