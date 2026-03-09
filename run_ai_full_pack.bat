@echo off
setlocal

cd /d %~dp0

if not exist .venv (
  py -3.12 -m venv .venv
)

call .\.venv\Scripts\activate.bat
python -m pip install -U pip
python -m pip install -e .

python -m tamacore.cli ai-full-pack --out assets/packs/ai_pack_full --shop-count 5 --foods 5 --cosmetics 5

endlocal
pause
