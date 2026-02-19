# TamaCore Pipeline (PDF -> assets -> mapping.json) for GDevelop

## What this does
- Extracts images from: input/TamaCore_Game_Design_WITH_IMAGES.pdf
- Collects everything to: output/assets_raw/_drop_all
- Classifies assets into folders: ui/cosmetics/effects/backgrounds/pet/_unmapped
- Generates: output/assets_raw/mapping.json

## Quick start (NO PowerShell typing)
1) Put your PDF here:
   input/TamaCore_Game_Design_WITH_IMAGES.pdf

2) Optional: put extra images here:
   input/extra_images/

3) Double-click:
   run.bat

## Output
- output/assets_raw/_drop_all/
- output/assets_raw/ui/
- output/assets_raw/cosmetics/
- output/assets_raw/effects/
- output/assets_raw/backgrounds/
- output/assets_raw/pet/
- output/assets_raw/_unmapped/
- output/assets_raw/mapping.json

## Notes
- Don’t type Python code in terminal.
- This repo is designed to run with one file: run.bat
