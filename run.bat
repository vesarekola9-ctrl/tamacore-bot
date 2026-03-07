@echo off
setlocal

cd /d %~dp0

if not exist .venv (
  py -3.12 -m venv .venv
)

call .\.venv\Scripts\activate.bat
python -m pip install -U pip
python -m pip install -e .

python -m tamacore.cli make-game --v31 --v32 --pack assets/packs/demo_pack --template templates/gdevelop_template --out ..\tamacore-game --with-demo-layout --export-out exports --export-web --export-zip --bundle-release --bundle-out release_bundle
if errorlevel 1 goto :fail

python -m tamacore.cli validate --game-dir ..\tamacore-game
if errorlevel 1 goto :fail

python -m tamacore.cli validate-exports --export-dir exports
if errorlevel 1 goto :fail

echo [OK] TamaCore pipeline complete
goto :end

:fail
echo [ERR] TamaCore pipeline failed

:end
endlocal
pause
