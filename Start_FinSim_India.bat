@echo off
setlocal
title FinSim India

set "SOURCE=%~dp0"
set "WEBROOT=%TEMP%\FinSimIndiaLocal"
set "APP=%WEBROOT%\FinSim-India"

if not exist "%SOURCE%index.html" (
  echo ERROR: index.html was not found.
  echo Extract the complete FinSim India ZIP, then run this BAT from that folder.
  pause
  exit /b 1
)
if not exist "%SOURCE%service-worker.js" (
  echo ERROR: service-worker.js was not found.
  echo Please extract the complete FinSim India ZIP before running this BAT.
  pause
  exit /b 1
)
if not exist "%SOURCE%manifest.webmanifest" (
  echo ERROR: manifest.webmanifest was not found.
  pause
  exit /b 1
)

if exist "%APP%" rmdir /s /q "%APP%"
mkdir "%APP%\icons" 2>nul
mkdir "%APP%\data" 2>nul

copy /y "%SOURCE%index.html" "%APP%\index.html" >nul
copy /y "%SOURCE%service-worker.js" "%APP%\service-worker.js" >nul
copy /y "%SOURCE%manifest.webmanifest" "%APP%\manifest.webmanifest" >nul

if exist "%SOURCE%icons" xcopy "%SOURCE%icons\*" "%APP%\icons\" /e /i /y >nul
if exist "%SOURCE%data\market-quotes.json" copy /y "%SOURCE%data\market-quotes.json" "%APP%\data\market-quotes.json" >nul

where py >nul 2>nul
if not errorlevel 1 (
  start "FinSim India Server" /min py -m http.server 5500 --bind 127.0.0.1 --directory "%WEBROOT%"
  goto OPEN_APP
)

where python >nul 2>nul
if not errorlevel 1 (
  start "FinSim India Server" /min python -m http.server 5500 --bind 127.0.0.1 --directory "%WEBROOT%"
  goto OPEN_APP
)

echo Python was not found on this PC.
echo Install Python from https://www.python.org/downloads/ and try again.
pause
exit /b 1

:OPEN_APP
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:5500/FinSim-India/"
echo.
echo FinSim India is opening in your browser.
echo Keep the minimized server window open while using FinSim.
echo Close that server window to stop the local website.
echo.
exit /b 0
