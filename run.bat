@echo off
setlocal

cd /d %~dp0

if not exist .venv (
  py -3.12 -m venv .venv
)

call .\.venv\Scripts\activate.bat
python -m pip install -U pip
python -m pip install -e .

python -m tamacore.cli inspect-pack --pack assets/packs/demo_pack
if errorlevel 1 goto :fail

python -m tamacore.cli build --v31 --v32 --pack assets/packs/demo_pack --template templates/gdevelop_template --out ..\tamacore-game --with-demo-layout
if errorlevel 1 goto :fail

python -m tamacore.cli validate --game-dir ..\tamacore-game
if errorlevel 1 goto :fail

echo [OK] Build complete
goto :end

:fail
echo [ERR] Build failed

:end
endlocal
pause
