@echo off
echo ================================
echo   ACE-Codex Backend Launcher
echo ================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install from https://python.org
    pause
    exit /b 1
)

REM Check Ollama
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Ollama not detected. Start it with: ollama serve
    echo.
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet

REM Start backend
echo.
echo Starting ACE-Codex backend on http://localhost:5005...
echo.
python -m src.extension

pause
