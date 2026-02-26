# TamaCore Bot (GDevelop MVP Producer) — NO DEPS

This repo generates/updates a minimal GDevelop project JSON and copies assets into a game folder.

✅ No external Python dependencies (no Pillow, no PyMuPDF). Works on very new Python versions.

## Local run (Windows PowerShell)
```powershell
cd C:\Users\vesa_\tamacore-bot
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

.\.venv\Scripts\python.exe run_pipeline.py --game-dir ..\tamacore-game
