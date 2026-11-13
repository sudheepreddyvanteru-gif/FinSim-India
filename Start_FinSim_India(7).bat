@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_CMD="
where py >nul 2>nul && set "PYTHON_CMD=py"
if not defined PYTHON_CMD where python >nul 2>nul && set "PYTHON_CMD=python"

if not defined PYTHON_CMD (
  echo Python 3 was not found on this PC.
  echo Install Python from https://www.python.org/downloads/ and try again.
  pause
  exit /b 1
)

start "FinSim India local server" cmd /k "cd /d ""%~dp0"" && %PYTHON_CMD% -m http.server 5500 --bind 127.0.0.1"
timeout /t 2 /nobreak >nul
start "" "http://localhost:5500/FinSim_India.html"
echo.
echo FinSim India is running at http://localhost:5500/FinSim_India.html
echo Keep the server window open while using the app.
endlocal
