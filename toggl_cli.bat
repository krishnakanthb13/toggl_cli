@echo off
REM Toggl Time Tracker Launcher
REM This batch file launches the Toggl CLI Python script

REM REM Check if Python is installed
REM python --version >nul 2>&1
REM if errorlevel 1 (
    REM echo Error: Python is not installed or not in PATH
    REM echo Please install Python from https://www.python.org/
    REM pause
    REM exit /b 1
REM )

REM REM Check if requests library is installed
REM python -c "import requests" >nul 2>&1
REM if errorlevel 1 (
    REM echo Installing required Python package: requests...
    REM python -m pip install requests
    REM if errorlevel 1 (
        REM echo Error: Failed to install requests package
        REM echo Please run: pip install requests
        REM pause
        REM exit /b 1
    REM )
REM )

REM Run the Toggl CLI
python toggl_cli.py %*

REM Keep window open if there was an error
if errorlevel 1 pause

exit /b 0
