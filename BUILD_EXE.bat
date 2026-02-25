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
if exist dist_console rmdir /s /q dist_console
if exist dist_gui rmdir /s /q dist_gui
if exist TamaCoreBot.spec del /q TamaCoreBot.spec
if exist TamaCoreBotGUI.spec del /q TamaCoreBotGUI.spec

REM Build console exe (debug)
python -m PyInstaller ^
  --clean ^
  --onefile ^
  --name TamaCoreBot ^
  --distpath dist_console ^
  --add-data "tools;tools" ^
  run_pipeline.py

REM Build GUI exe (no console)
python -m PyInstaller ^
  --clean ^
  --onefile ^
  --noconsole ^
  --name TamaCoreBotGUI ^
  --distpath dist_gui ^
  --add-data "tools;tools" ^
  gui_app.py

echo.
echo DONE:
echo - %cd%\dist_console\TamaCoreBot.exe
echo - %cd%\dist_gui\TamaCoreBotGUI.exe
echo.
pause
