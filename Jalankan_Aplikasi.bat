@echo off
echo Starting App...

set "PYTHON_CMD=python"
python --version >nul 2>&1
if errorlevel 1 (
    set "PYTHON_CMD=py"
    py --version >nul 2>&1
    if errorlevel 1 (
        echo Error: Python not found! Please install Python.
        pause
        exit /b
    )
)

%PYTHON_CMD% -m pip install -r requirements.txt >nul 2>&1
start "" cmd /c "timeout /t 4 >nul & start http://127.0.0.1:5000/"
%PYTHON_CMD% app.py
pause
