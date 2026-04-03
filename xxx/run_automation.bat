@echo off
echo.
echo 🚀 EMAIL AUTOMATION SYSTEM
echo ========================
echo.
echo Choose an option:
echo 1. Manage Email List
echo 2. Send Emails
echo 3. Exit
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    python email_manager.py
    pause
) else if "%choice%"=="2" (
    python email_automation.py
    pause
) else (
    echo Goodbye!
    timeout 2 > nul
)
