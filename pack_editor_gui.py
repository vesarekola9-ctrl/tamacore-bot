from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from tamacore.factory_v3_1.pack_editor import (
    create_default_pack,
    load_pack,
    save_pack,
)

ROOT = Path(__file__).resolve().parent


class PackEditor(tk.Tk):

    def __init__(self) -> None:
        super().__init__()

        self.title("TamaCore Pack Editor")
        self.geometry("600x420")

        self.pack_dir = tk.StringVar(value=str(ROOT / "assets" / "packs" / "demo_pack"))
        self.name_var = tk.StringVar()
        self.levels_var = tk.StringVar()
        self.coins_var = tk.StringVar()
        self.enemies_var = tk.StringVar()

        self._build_ui()

    def _build_ui(self):

        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frame, text="Pack folder").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.pack_dir, width=40).grid(row=0, column=1)
        ttk.Button(frame, text="Browse", command=self.browse).grid(row=0, column=2)

        ttk.Label(frame, text="Name").grid(row=1, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.name_var).grid(row=1, column=1)

        ttk.Label(frame, text="Levels").grid(row=2, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.levels_var).grid(row=2, column=1)

        ttk.Label(frame, text="Coins").grid(row=3, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.coins_var).grid(row=3, column=1)

        ttk.Label(frame, text="Enemies").grid(row=4, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.enemies_var).grid(row=4, column=1)

        ttk.Button(frame, text="Load", command=self.load).grid(row=5, column=0)
        ttk.Button(frame, text="Save", command=self.save).grid(row=5, column=1)
        ttk.Button(frame, text="New", command=self.new).grid(row=5, column=2)

    def browse(self):
        path = filedialog.askdirectory()
        if path:
            self.pack_dir.set(path)

    def load(self):
        data = load_pack(Path(self.pack_dir.get()))
        if not data:
            messagebox.showerror("Error", "pack.json not found")
            return

        self.name_var.set(data.get("name", ""))
        self.levels_var.set(str(data.get("levels", {}).get("count", 1)))
        self.coins_var.set(str(data.get("coinSpawn", {}).get("count", 0)))
        self.enemies_var.set(str(data.get("enemySpawn", {}).get("count", 0)))

    def save(self):
        pack_dir = Path(self.pack_dir.get())

        data = load_pack(pack_dir)

        if not data:
            data = create_default_pack(self.name_var.get())

        data["name"] = self.name_var.get()
        data["levels"]["count"] = int(self.levels_var.get())
        data["coinSpawn"]["count"] = int(self.coins_var.get())
        data["enemySpawn"]["count"] = int(self.enemies_var.get())

        save_pack(pack_dir, data)

        messagebox.showinfo("OK", "Saved")

    def new(self):
        data = create_default_pack("New Pack")
        save_pack(Path(self.pack_dir.get()), data)
        self.load()


if __name__ == "__main__":
    app = PackEditor()
    app.mainloop()
