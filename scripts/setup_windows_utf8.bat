@echo off
REM Windows UTF-8 System Setup (Batch version)
REM This script sets UTF-8 encoding for the current session and user environment

echo Setting up UTF-8 encoding for Windows...
echo.

REM Set environment variable for current user
echo Setting PYTHONIOENCODING=utf-8 for current user...
setx PYTHONIOENCODING utf-8 > nul

REM Set console code page to UTF-8
echo Setting console code page to UTF-8...
chcp 65001 > nul

REM Set environment variables for current session
set PYTHONIOENCODING=utf-8
set LANG=en_US.UTF-8

echo.
echo ✅ UTF-8 setup complete!
echo.
echo Please restart Command Prompt/PowerShell to make changes permanent.
echo.
echo Testing Unicode in current session:
python -c "print('🚀 Unicode test: 💻🔥👨‍💻🌟')"

echo.
echo To use UTF-8 in future sessions, run this batch file or restart your terminal.
pause