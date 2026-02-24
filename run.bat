@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================
echo TamaCore Bot – FULL PIPELINE (PRO+)
echo ============================================
echo.

echo [1/10] Creating virtual environment if missing...
if not exist ".venv" (
  py -m venv .venv
)

echo [2/10] Ensuring pip...
call ".venv\Scripts\python.exe" -m ensurepip --upgrade >nul 2>&1

echo [3/10] Installing / updating dependencies...
call ".venv\Scripts\python.exe" -m pip install --upgrade pip
call ".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo.
echo ============================================
echo Running TamaCore Pipeline
echo ============================================
echo.

echo [4/10] Preparing folders...
call ".venv\Scripts\python.exe" tools\make_folders.py

echo [5/10] Extracting images from PDF...
call ".venv\Scripts\python.exe" tools\extract_from_pdf.py

echo [6/10] Scanning + mapping assets...
call ".venv\Scripts\python.exe" tools\asset_scan_and_map.py

echo [7/10] Naming PRO + Dedupe + Soft Validate...
call ".venv\Scripts\python.exe" tools\naming_pro.py
call ".venv\Scripts\python.exe" tools\dedupe.py
call ".venv\Scripts\python.exe" tools\soft_validate.py

echo [8/10] Building texture atlas...
call ".venv\Scripts\python.exe" tools\atlas_pack.py

echo [9/10] Generating GDevelop pack...
call ".venv\Scripts\python.exe" tools\gdevelop_pack_generate.py

echo [10/10] Generating game scaffold (Home/Shop/Inventory + systems)...
call ".venv\Scripts\python.exe" tools\game_scaffold_generate.py

echo.
echo ============================================
echo [OK] DONE
echo ============================================
echo.
echo Check folders:
echo output\assets_raw\
echo output\atlas\
echo output\gdevelop_pack\
echo output\scaffold\
echo output\reports\
echo.
pause
