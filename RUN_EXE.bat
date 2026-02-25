@echo off
cd /d "%~dp0"

if not exist "dist\TamaCoreBot.exe" (
  echo EXE missing. Run BUILD_EXE.bat first.
  pause
  exit /b 1
)

dist\TamaCoreBot.exe
pause
