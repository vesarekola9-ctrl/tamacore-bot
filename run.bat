@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo ============================================
echo TamaCore Bot – FULL PIPELINE
echo ============================================
echo.

echo [1/6] Creating virtual environment if missing...
if not exist ".venv" (
    py -m venv .venv
)

echo [2/6] Ensuring pip...
call ".venv\Scripts\python.exe" -m ensurepip --upgrade >nul 2>&1

echo [3/6] Installing / updating dependencies...
call ".venv\Scripts\python.exe" -m pip install --upgrade pip
call ".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo.
echo ============================================
echo Running TamaCore Pipeline
echo ============================================
echo.

echo [4/6] Preparing folders...
call ".venv\Scripts\python.exe" tools\make_folders.py

echo [5/6] Extracting images from PDF...
call ".venv\Scripts\python.exe" tools\extract_from_pdf.py

echo [6/6] Scanning + mapping assets...
call ".venv\Scripts\python.exe" tools\asset_scan_and_map.py

echo [7/6] Building texture atlas...
call ".venv\Scripts\python.exe" tools\atlas_pack.py

echo [8/6] Generating GDevelop pack...
call ".venv\Scripts\python.exe" tools\gdevelop_pack_generate.py

echo.
echo ============================================
echo [OK] DONE
echo ============================================
echo.
echo Check these folders:
echo   output\assets_raw\
echo   output\atlas\
echo   output\gdevelop_pack\
echo.

pause
