@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python was not found on this PC.
    echo Install Python, or open this folder in VS Code and use Live Server.
    pause
    exit /b 1
  )
  set "PYTHON_CMD=python"
) else (
  set "PYTHON_CMD=py"
)
start "FinSim India local server" cmd /k "cd /d ""%~dp0"" && %PYTHON_CMD% -m http.server 5500 --bind 127.0.0.1"
timeout /t 2 /nobreak >nul
start "" "http://localhost:5500/FinSim_India.html"
echo.
echo FinSim India is running at http://localhost:5500/FinSim_India.html
echo Keep the server window open while using the app.
endlocal
