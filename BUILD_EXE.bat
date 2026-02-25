@echo off
cd /d "%~dp0"

call .venv\Scripts\activate

python -m pip install --upgrade pip
python -m pip install pyinstaller

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist TamaCoreBot.spec del TamaCoreBot.spec

python -m PyInstaller ^
  --clean ^
  --onefile ^
  --name TamaCoreBot ^
  --add-data "tools;tools" ^
  run_pipeline.py

pause
