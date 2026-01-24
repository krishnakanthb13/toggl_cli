@echo off
title Toggl CLI Manager

:menu
cls
echo ============================================================
echo                  Toggl CLI Manager
echo ============================================================
echo.
echo     1. Run Toggl CLI (Interactive)
echo     2. Reviewer - Toggl Reports (Port 8086)
echo     0. Exit
echo.
set /p choice="Enter your choice (0-2): "

if "%choice%"=="1" goto runcli
if "%choice%"=="2" goto reviewer
if "%choice%"=="0" goto end
goto menu

:runcli
cls
echo Starting Toggl CLI...
echo.
python toggl_cli.py
pause
goto menu

:reviewer
setlocal
cd /d "%~dp0"

echo Starting Toggl Reviewer...
echo.

REM Launch a background task to wait for the port to be active
echo Waiting for server to start...
start /b powershell -noprofile -command "$client = New-Object System.Net.Sockets.TcpClient; $maxRetries = 20; $retryCount = 0; $connected = $false; while (-not $connected -and $retryCount -lt $maxRetries) { try { $client.Connect('localhost', 8086); $connected = $true; $client.Close() } catch { Start-Sleep -Milliseconds 500; $retryCount++ } }; if ($connected) { Start-Process 'http://localhost:8086/toggl_cli_review.html' }"

echo Starting server on port 8086...
echo.
echo Server is running. Press Ctrl+C to stop the server.
echo.

REM Detect and run server
where http-server >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Using http-server (Node.js)
    call http-server -a 127.0.0.1 -p 8086 -c-1
    goto SERVER_DONE
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Using Python server
    python -m http.server 8086 --bind 127.0.0.1
    goto SERVER_DONE
)

where python3 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Using Python3 server
    python3 -m http.server 8086 --bind 127.0.0.1
    goto SERVER_DONE
)

echo.
echo [ERROR] No server engine found!
echo Please install Python (python.org) or Node.js (nodejs.org).
echo.
pause
goto menu

:SERVER_DONE
echo.
echo Server stopped. Press Enter to return to menu.
pause > nul
goto menu

:end
exit