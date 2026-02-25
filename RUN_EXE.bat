@echo off
cd /d "%~dp0"

if not exist dist\TamaCoreBot.exe (
    echo EXE missing → run BUILD_EXE.bat first
    pause
    exit /b
)

dist\TamaCoreBot.exe
pause
