@echo off
REM OAKAI Document Reader - Portable Server
REM v2.2 - Fixed UI with Settings page

echo Starting OAKAI Document Reader...
echo Access at: http://localhost:8765
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"

REM Check Python
python.exe --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM Start the server
python.exe doc_reader_onefile.py

pause
