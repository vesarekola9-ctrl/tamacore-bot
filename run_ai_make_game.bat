@echo off
setlocal

cd /d %~dp0

if not exist .venv (
  py -3.12 -m venv .venv
)

call .\.venv\Scripts\activate.bat
python -m pip install -U pip
python -m pip install -e .

python -m tamacore.cli ai-make-game --out-pack assets/packs/ai_game_1 --template templates/gdevelop_template --out-game ..\tamacore-game --export-out exports --bundle-out release_bundle --shop-count 5 --foods 5 --cosmetics 5 --with-demo-layout

endlocal
pause
