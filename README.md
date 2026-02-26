# TamaCore Bot (GDevelop MVP Producer)

This repo generates/updates a minimal GDevelop project JSON and copies assets into a game folder.

## Local Quick Start (Windows PowerShell)

```powershell
cd C:\Users\vesa_\tamacore-bot
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Produce/update game in tamacore-game
.\.venv\Scripts\python.exe run_pipeline.py --game-dir ..\tamacore-game
