@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo [1/5] Creating venv if missing...
if not exist ".venv" (
  py -m venv .venv
)

echo [2/5] Ensuring pip...
call ".venv\Scripts\python.exe" -m ensurepip --upgrade >nul 2>&1

echo [3/5] Installing requirements...
call ".venv\Scripts\python.exe" -m pip install --upgrade pip
call ".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo [4/5] Running pipeline...
call ".venv\Scripts\python.exe" tools\make_folders.py
call ".venv\Scripts\python.exe" tools\extract_from_pdf.py
call ".venv\Scripts\python.exe" tools\ingest_extra_images.py
call ".venv\Scripts\python.exe" tools\asset_scan_and_map.py

echo.
echo [OK] Done. Check output\assets_raw\mapping.json
pause
