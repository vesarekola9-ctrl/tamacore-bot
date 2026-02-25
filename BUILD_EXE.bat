@echo off
cd /d "%~dp0"

if not exist ".venv" (
  py -m venv .venv
)

call .venv\Scripts\activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist TamaCoreBot.spec del /q TamaCoreBot.spec

python -m PyInstaller ^
  --clean ^
  --onefile ^
  --name TamaCoreBot ^
  --add-data "tools;tools" ^
  run_pipeline.py

echo.
echo EXE ready: %cd%\dist\TamaCoreBot.exe
echo Tip: You can copy TamaCoreBot.exe anywhere (Desktop/USB) and it will create input/output next to it.
echo.
pause
