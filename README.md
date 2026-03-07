# TamaCore Bot

TamaCore builds a GDevelop-ready game project from a pack.

## Build

```bash
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -U pip
.\.venv\Scripts\python.exe -m pip install -e .
tamacore build --v31 --v32 --pack assets/packs/demo_pack --out ..\tamacore-game --with-demo-layout
