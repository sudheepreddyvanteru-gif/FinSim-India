@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_CMD="
where py >nul 2>nul && set "PYTHON_CMD=py"
if not defined PYTHON_CMD where python >nul 2>nul && set "PYTHON_CMD=python"

if not defined PYTHON_CMD (
  echo Python was not found on this PC.
  echo Install Python 3 from https://www.python.org/downloads/
  echo Then double-click this file again.
  pause
  exit /b 1
)

set "PORT=5500"
echo Starting FinSim India on http://127.0.0.1:%PORT%/
start "FinSim India local server" cmd /k "cd /d ""%~dp0"" && %PYTHON_CMD% -m http.server %PORT% --bind 127.0.0.1"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:%PORT%/FinSim_India.html"

echo.
echo Keep the FinSim India server window open while using the app.
endlocal
