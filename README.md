# TamaCore Bot — GDevelop Template Patcher (NO PDF, NO PyMuPDF)

This repo generates a playable GDevelop project by:
1) copying a real GDevelop project template, then
2) patching its `game.json` to add resources/objects/instances.

✅ No Python dependencies (stdlib only). Works even on very new Python.

---

## 1) Create the template (ONE-TIME)
In GDevelop:
- Create new project → Empty
- Save As folder: `templates/gdevelop_template` (inside this repo)
- Close GDevelop

You MUST have:
- `templates/gdevelop_template/game.json`

Commit the template folder to GitHub.

---

## 2) Put assets
Place your images in `assets/`:
- `player.png`
- `coin.png`
- `bg.png`
(or any other images; they are copied too)

If assets folder has no images, the bot will create tiny placeholder PNGs.

---

## 3) Run locally
```powershell
cd C:\Users\vesa_\tamacore-bot
python run_pipeline.py --game-dir ..\tamacore-game
