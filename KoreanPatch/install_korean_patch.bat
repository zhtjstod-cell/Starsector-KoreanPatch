@echo off
setlocal
cd /d "%~dp0"
set "PYTHON_CMD="

where py >nul 2>nul
if not errorlevel 1 (
    py -3 -c "import sys" >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=py -3"
)

if not defined PYTHON_CMD (
    where python >nul 2>nul
    if not errorlevel 1 (
        python -c "import sys; raise SystemExit(0 if sys.version_info[0] == 3 else 1)" >nul 2>nul
        if not errorlevel 1 set "PYTHON_CMD=python"
    )
)

if not defined PYTHON_CMD (
    echo Python 3 was not found.
    echo Install Python 3, or fix the Python launcher/PATH setting.
    echo If Python is already installed, try: py -0p
    pause
    exit /b 1
)

%PYTHON_CMD% -X utf8 "%~dp0install_korean_patch.py" %*
set "RC=%ERRORLEVEL%"
pause
exit /b %RC%
