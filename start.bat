@echo off
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python ga install sarete imasen.
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

if not exist ".venv" (
    echo [SETUP] venv wo sakusei shite imasu...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo [SETUP] package wo install shite imasu...
    python -m pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

echo.
echo ============================================
echo  Zuimen Check System - Kido chu...
echo  http://localhost:8501
echo  LAN kyoyu: http://%COMPUTERNAME%:8501
echo  Shuryou: Ctrl+C
echo ============================================
echo.

python -m streamlit run src/app.py --server.address=0.0.0.0 --browser.gatherUsageStats=false

pause