# TamaCore Bot (GDevelop Game Producer)

Generates/updates a GDevelop project JSON and copies assets into a game folder.

## Quick start (Windows PowerShell)

```powershell
cd C:\Users\vesa_\tamacore-bot
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Produce/update game in tamacore-game
.\.venv\Scripts\python.exe run_pipeline.py --game-dir ..\tamacore-game
