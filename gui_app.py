from __future__ import annotations

import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


ROOT = Path(__file__).resolve().parent


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("TamaCore Bot")
        self.geometry("760x520")
        self.minsize(760, 520)

        self.pack_var = tk.StringVar(value=str(ROOT / "assets" / "packs" / "demo_pack"))
        self.template_var = tk.StringVar(value=str(ROOT / "templates" / "gdevelop_template"))
        self.out_var = tk.StringVar(value=str((ROOT.parent / "tamacore-game").resolve()))
        self.v31_var = tk.BooleanVar(value=True)
        self.v32_var = tk.BooleanVar(value=True)
        self.demo_layout_var = tk.BooleanVar(value=True)

        self._build_ui()

    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": 8}

        top = ttk.Frame(self)
        top.pack(fill="x", padx=12, pady=12)

        ttk.Label(top, text="Pack").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(top, textvariable=self.pack_var, width=70).grid(row=0, column=1, sticky="ew", **pad)
        ttk.Button(top, text="Browse", command=self._browse_pack).grid(row=0, column=2, **pad)

        ttk.Label(top, text="Template").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(top, textvariable=self.template_var, width=70).grid(row=1, column=1, sticky="ew", **pad)
        ttk.Button(top, text="Browse", command=self._browse_template).grid(row=1, column=2, **pad)

        ttk.Label(top, text="Output").grid(row=2, column=0, sticky="w", **pad)
        ttk.Entry(top, textvariable=self.out_var, width=70).grid(row=2, column=1, sticky="ew", **pad)
        ttk.Button(top, text="Browse", command=self._browse_out).grid(row=2, column=2, **pad)

        top.columnconfigure(1, weight=1)

        opts = ttk.LabelFrame(self, text="Options")
        opts.pack(fill="x", padx=12, pady=(0, 12))

        ttk.Checkbutton(opts, text="v3.1", variable=self.v31_var).pack(anchor="w", padx=10, pady=6)
        ttk.Checkbutton(opts, text="v3.2", variable=self.v32_var).pack(anchor="w", padx=10, pady=6)
        ttk.Checkbutton(opts, text="With demo layout", variable=self.demo_layout_var).pack(anchor="w", padx=10, pady=6)

        actions = ttk.Frame(self)
        actions.pack(fill="x", padx=12, pady=(0, 12))

        ttk.Button(actions, text="Build Game", command=self._build_game).pack(side="left", padx=6)
        ttk.Button(actions, text="Open Output Folder", command=self._open_output).pack(side="left", padx=6)
        ttk.Button(actions, text="Open game.json", command=self._open_game_json).pack(side="left", padx=6)

        log_frame = ttk.LabelFrame(self, text="Log")
        log_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.log = tk.Text(log_frame, wrap="word", height=18)
        self.log.pack(fill="both", expand=True, padx=8, pady=8)

    def _browse_pack(self) -> None:
        path = filedialog.askdirectory(initialdir=self.pack_var.get() or str(ROOT))
        if path:
            self.pack_var.set(path)

    def _browse_template(self) -> None:
        path = filedialog.askdirectory(initialdir=self.template_var.get() or str(ROOT))
        if path:
            self.template_var.set(path)

    def _browse_out(self) -> None:
        path = filedialog.askdirectory(initialdir=self.out_var.get() or str(ROOT))
        if path:
            self.out_var.set(path)

    def _append_log(self, text: str) -> None:
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.update_idletasks()

    def _build_game(self) -> None:
        pack_dir = Path(self.pack_var.get())
        template_dir = Path(self.template_var.get())
        out_dir = Path(self.out_var.get())

        cmd = [
            sys.executable,
            "-m",
            "tamacore.cli",
            "build",
            "--pack",
            str(pack_dir),
            "--template",
            str(template_dir),
            "--out",
            str(out_dir),
        ]

        if self.demo_layout_var.get():
            cmd.append("--with-demo-layout")
        if self.v31_var.get():
            cmd.append("--v31")
        if self.v32_var.get():
            cmd.append("--v32")

        self._append_log(" ".join(cmd))

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception as exc:
            messagebox.showerror("Build failed", str(exc))
            self._append_log(f"[ERR] {exc}")
            return

        if proc.stdout:
            self._append_log(proc.stdout.rstrip())
        if proc.stderr:
            self._append_log(proc.stderr.rstrip())

        if proc.returncode == 0:
            self._append_log("[OK] Build completed")
            messagebox.showinfo("TamaCore", "Build completed")
        else:
            self._append_log(f"[ERR] Exit code {proc.returncode}")
            messagebox.showerror("TamaCore", f"Build failed with exit code {proc.returncode}")

    def _open_output(self) -> None:
        out_dir = Path(self.out_var.get())
        out_dir.mkdir(parents=True, exist_ok=True)

        try:
            if sys.platform.startswith("win"):
                subprocess.Popen(["explorer", str(out_dir)])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(out_dir)])
            else:
                subprocess.Popen(["xdg-open", str(out_dir)])
        except Exception as exc:
            messagebox.showerror("Open output failed", str(exc))

    def _open_game_json(self) -> None:
        game_json = Path(self.out_var.get()) / "game.json"
        if not game_json.exists():
            messagebox.showwarning("Missing file", f"Not found: {game_json}")
            return

        try:
            if sys.platform.startswith("win"):
                subprocess.Popen(["cmd", "/c", "start", "", str(game_json)])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(game_json)])
            else:
                subprocess.Popen(["xdg-open", str(game_json)])
        except Exception as exc:
            messagebox.showerror("Open game.json failed", str(exc))


if __name__ == "__main__":
    app = App()
    app.mainloop()
