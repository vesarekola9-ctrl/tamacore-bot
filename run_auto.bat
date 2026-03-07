@echo off
setlocal

cd /d %~dp0

if not exist .venv (
  py -3.12 -m venv .venv
)

call .\.venv\Scripts\activate.bat
python -m pip install -U pip
python -m pip install -e .

python -m tamacore.cli auto --workspace auto_workspace --template templates/gdevelop_template --pack-name auto_pack --game-name auto_game

endlocal
pause
