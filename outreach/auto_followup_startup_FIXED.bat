@echo off
REM =================================================================
REM AUTO FOLLOWUP BOT - FIXED UNICODE VERSION
REM Handles Unicode characters and emojis properly
REM =================================================================

REM Set UTF-8 encoding to handle emojis and Unicode
chcp 65001 >nul 2>&1

title Auto Followup Bot - Startup

REM ========== CONFIGURATION SECTION ==========
REM CHANGE THESE PATHS TO MATCH YOUR SETUP:
set SCRIPT_DIR=C:\Users\Mayank\Desktop\outreach
set PYTHON_SCRIPT=smart_followup_automation_final.py
set LOG_FILE=%SCRIPT_DIR%\auto_followup_log.txt

REM ========== LOG INITIALIZATION ==========
if not exist "%SCRIPT_DIR%" mkdir "%SCRIPT_DIR%"
echo. >> "%LOG_FILE%"
echo ================================================================= >> "%LOG_FILE%"
echo AUTO FOLLOWUP BOT STARTUP LOG >> "%LOG_FILE%"
echo Started at: %DATE% %TIME% >> "%LOG_FILE%"
echo ================================================================= >> "%LOG_FILE%"

REM Change to script directory
cd /d "%SCRIPT_DIR%"

REM ========== INTERNET CONNECTION WAIT ==========
echo Waiting for internet connection...
echo Checking internet connection... >> "%LOG_FILE%"

:CheckInternet
REM Try multiple reliable servers
ping -n 1 8.8.8.8 >nul 2>&1
if not errorlevel 1 goto InternetOK

ping -n 1 1.1.1.1 >nul 2>&1
if not errorlevel 1 goto InternetOK

ping -n 1 google.com >nul 2>&1
if not errorlevel 1 goto InternetOK

echo No internet connection, retrying in 15 seconds...
echo No internet at %TIME% - retrying... >> "%LOG_FILE%"
timeout /t 15 /nobreak >nul
goto CheckInternet

:InternetOK
echo Internet connection established!
echo Internet connected at: %TIME% >> "%LOG_FILE%"

REM Give additional time for stable connection
echo Waiting 20 seconds for stable connection...
timeout /t 20 /nobreak >nul

REM ========== PYTHON & FILE VALIDATION ==========
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! >> "%LOG_FILE%"
    echo Install Python and add to PATH >> "%LOG_FILE%"
    echo Python not found! Please install Python.
    goto ErrorExit
)

if not exist "%PYTHON_SCRIPT%" (
    echo ERROR: Script not found: %PYTHON_SCRIPT% >> "%LOG_FILE%"
    echo Please copy smart_followup_automation_final.py to %SCRIPT_DIR% >> "%LOG_FILE%"
    echo Bot script not found! Check path: %SCRIPT_DIR%\%PYTHON_SCRIPT%
    goto ErrorExit
)

if not exist "gmail_config.txt" (
    echo ERROR: gmail_config.txt not found >> "%LOG_FILE%"
    echo Please create gmail_config.txt with your credentials >> "%LOG_FILE%"
    echo Gmail config file missing!
    goto ErrorExit
)

if not exist "email_list.csv" (
    echo ERROR: email_list.csv not found >> "%LOG_FILE%"
    echo Please create your email list first >> "%LOG_FILE%"
    echo Email list file missing!
    goto ErrorExit
)

REM ========== START AUTO FOLLOWUP BOT ==========
echo Starting Auto Followup Bot...
echo Starting auto followup bot at: %TIME% >> "%LOG_FILE%"

REM Set environment variables to handle Unicode properly
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=utf-8

REM Use echo to automatically select option 1 (Process follow-ups)
REM This sends "1" as input to the Python script
echo 1 | python "%PYTHON_SCRIPT%" >> "%LOG_FILE%" 2>&1

REM Check if the script ran successfully
if %ERRORLEVEL% EQU 0 (
    echo Followup bot completed successfully >> "%LOG_FILE%"
    echo Followup processing completed successfully!
) else (
    echo Followup bot failed with error code: %ERRORLEVEL% >> "%LOG_FILE%"
    echo Bot encountered an error! Check log file: %LOG_FILE%
    goto ErrorExit
)

REM ========== SUCCESS COMPLETION ==========
echo Bot finished successfully at: %TIME% >> "%LOG_FILE%"
echo ================================== >> "%LOG_FILE%"
echo.
echo SUCCESS: Followup bot completed!
echo Check the log file for details: %LOG_FILE%
echo.
echo The bot will now close in 5 seconds...
timeout /t 5 /nobreak >nul
exit /b 0

:ErrorExit
echo.
echo ERROR: Bot failed to run properly!
echo Check the log file: %LOG_FILE%
echo.
pause
exit /b 1
