# TamaCore Bot (Asset pipeline -> GDevelop)

Tämä repo tekee:
1) kansiorakenteen
2) PDF:stä upotettujen kuvien extraction -> output/assets_raw/_drop_all
3) automaattisen luokittelun -> ui/cosmetics/effects/backgrounds/pet/_unmapped + mapping.json
4) texture atlasin (atlas.png + atlas.json) GDevelopiin

## Rakenne
- input/  (tänne PDF: TamaCore_Game_Design_WITH_IMAGES.pdf)
- output/assets_raw/_drop_all  (extractatut kuvat)
- output/assets_raw/{ui,cosmetics,effects,backgrounds,pet,_unmapped}
- output/atlas/atlas.png + atlas.json

## Ajo (Windows / PowerShell)
ÄLÄ kirjoita python-koodia suoraan PowerShelliin (import jne).
Aja aina scriptit näin:

1) Luo venv ja asenna:
py -m venv .venv
.\.venv\Scripts\activate
py -m pip install -r requirements.txt

2) Laita PDF:
input/TamaCore_Game_Design_WITH_IMAGES.pdf

3) Aja pipeline:
py tools\make_folders.py
py tools\extract_from_pdf.py
py tools\asset_scan_and_map.py
py tools\atlas_pack.py

Valmista:
- output/assets_raw/mapping.json
- output/atlas/atlas.png + output/atlas/atlas.json

## GDevelop (Spritesheet)
GDevelopissa:
- Add resource -> Image -> lisää atlas.png
- Spritesheet/Atlas JSON -> valitse atlas.json (TexturePacker-tyylinen)
- Luo sprite-objekteja frame-nimillä (json -> frames -> filename)
