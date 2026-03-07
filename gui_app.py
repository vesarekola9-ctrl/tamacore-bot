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
        self.geometry("860x620")
        self.minsize(860, 620)

        self.pack_var = tk.StringVar(value=str(ROOT / "assets" / "packs" / "demo_pack"))
        self.template_var = tk.StringVar(value=str(ROOT / "templates" / "gdevelop_template"))
        self.out_var = tk.StringVar(value=str((ROOT.parent / "tamacore-game").resolve()))
        self.export_var = tk.StringVar(value=str((ROOT / "exports").resolve()))
        self.v31_var = tk.BooleanVar(value=True)
        self.v32_var = tk.BooleanVar(value=True)
        self.demo_layout_var = tk.BooleanVar(value=True)
        self.export_web_var = tk.BooleanVar(value=True)
        self.export_zip_var = tk.BooleanVar(value=True)
        self.export_android_var = tk.BooleanVar(value=False)

        self._build_ui()

    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": 8}

        top = ttk.Frame(self)
        top.pack(fill="x", padx=12, pady=12)

        ttk.Label(top, text="Pack").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(top, textvariable=self.pack_var, width=78).grid(row=0, column=1, sticky="ew", **pad)
        ttk.Button(top, text="Browse", command=self._browse_pack).grid(row=0, column=2, **pad)

        ttk.Label(top, text="Template").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(top, textvariable=self.template_var, width=78).grid(row=1, column=1, sticky="ew", **pad)
        ttk.Button(top, text="Browse", command=self._browse_template).grid(row=1, column=2, **pad)

        ttk.Label(top, text="Output").grid(row=2, column=0, sticky="w", **pad)
        ttk.Entry(top, textvariable=self.out_var, width=78).grid(row=2, column=1, sticky="ew", **pad)
        ttk.Button(top, text="Browse", command=self._browse_out).grid(row=2, column=2, **pad)

        ttk.Label(top, text="Export").grid(row=3, column=0, sticky="w", **pad)
        ttk.Entry(top, textvariable=self.export_var, width=78).grid(row=3, column=1, sticky="ew", **pad)
        ttk.Button(top, text="Browse", command=self._browse_export).grid(row=3, column=2, **pad)

        top.columnconfigure(1, weight=1)

        opts = ttk.LabelFrame(self, text="Build Options")
        opts.pack(fill="x", padx=12, pady=(0, 12))

        ttk.Checkbutton(opts, text="v3.1", variable=self.v31_var).pack(anchor="w", padx=10, pady=4)
        ttk.Checkbutton(opts, text="v3.2", variable=self.v32_var).pack(anchor="w", padx=10, pady=4)
        ttk.Checkbutton(opts, text="With demo layout", variable=self.demo_layout_var).pack(anchor="w", padx=10, pady=4)

        export_opts = ttk.LabelFrame(self, text="Export Options")
        export_opts.pack(fill="x", padx=12, pady=(0, 12))

        ttk.Checkbutton(export_opts, text="Web", variable=self.export_web_var).pack(anchor="w", padx=10, pady=4)
        ttk.Checkbutton(export_opts, text="ZIP", variable=self.export_zip_var).pack(anchor="w", padx=10, pady=4)
        ttk.Checkbutton(export_opts, text="Android stub", variable=self.export_android_var).pack(anchor="w", padx=10, pady=4)

        actions = ttk.Frame(self)
        actions.pack(fill="x", padx=12, pady=(0, 12))

        ttk.Button(actions, text="Make Game", command=self._make_game).pack(side="left", padx=6)
        ttk.Button(actions, text="Build Only", command=self._build_game).pack(side="left", padx=6)
        ttk.Button(actions, text="Inspect Pack", command=self._inspect_pack).pack(side="left", padx=6)
        ttk.Button(actions, text="Validate", command=self._validate_game).pack(side="left", padx=6)
        ttk.Button(actions, text="Open Output", command=self._open_output).pack(side="left", padx=6)
        ttk.Button(actions, text="Open Exports", command=self._open_exports).pack(side="left", padx=6)

        log_frame = ttk.LabelFrame(self, text="Log")
        log_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.log = tk.Text(log_frame, wrap="word", height=20)
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

    def _browse_export(self) -> None:
        path = filedialog.askdirectory(initialdir=self.export_var.get() or str(ROOT))
        if path:
            self.export_var.set(path)

    def _append_log(self, text: str) -> None:
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.update_idletasks()

    def _run_cmd(self, cmd: list[str]) -> int:
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
            self._append_log(f"[ERR] {exc}")
            messagebox.showerror("TamaCore", str(exc))
            return 1

        if proc.stdout:
            self._append_log(proc.stdout.rstrip())
        if proc.stderr:
            self._append_log(proc.stderr.rstrip())

        return proc.returncode

    def _inspect_pack(self) -> None:
        cmd = [
            sys.executable,
            "-m",
            "tamacore.cli",
            "inspect-pack",
            "--pack",
            str(Path(self.pack_var.get())),
        ]
        rc = self._run_cmd(cmd)
        if rc == 0:
            messagebox.showinfo("TamaCore", "Pack inspection passed")
        else:
            messagebox.showerror("TamaCore", f"Pack inspection failed with exit code {rc}")

    def _build_game(self) -> None:
        cmd = [
            sys.executable,
            "-m",
            "tamacore.cli",
            "build",
            "--pack",
            str(Path(self.pack_var.get())),
            "--template",
            str(Path(self.template_var.get())),
            "--out",
            str(Path(self.out_var.get())),
        ]
        if self.demo_layout_var.get():
            cmd.append("--with-demo-layout")
        if self.v31_var.get():
            cmd.append("--v31")
        if self.v32_var.get():
            cmd.append("--v32")

        rc = self._run_cmd(cmd)
        if rc == 0:
            messagebox.showinfo("TamaCore", "Build completed")
        else:
            messagebox.showerror("TamaCore", f"Build failed with exit code {rc}")

    def _make_game(self) -> None:
        cmd = [
            sys.executable,
            "-m",
            "tamacore.cli",
            "make-game",
            "--pack",
            str(Path(self.pack_var.get())),
            "--template",
            str(Path(self.template_var.get())),
            "--out",
            str(Path(self.out_var.get())),
            "--export-out",
            str(Path(self.export_var.get())),
        ]
        if self.demo_layout_var.get():
            cmd.append("--with-demo-layout")
        if self.v31_var.get():
            cmd.append("--v31")
        if self.v32_var.get():
            cmd.append("--v32")
        if self.export_web_var.get():
            cmd.append("--export-web")
        if self.export_zip_var.get():
            cmd.append("--export-zip")
        if self.export_android_var.get():
            cmd.append("--export-android")

        rc = self._run_cmd(cmd)
        if rc == 0:
            messagebox.showinfo("TamaCore", "Make Game completed")
        else:
            messagebox.showerror("TamaCore", f"Make Game failed with exit code {rc}")

    def _validate_game(self) -> None:
        cmd = [
            sys.executable,
            "-m",
            "tamacore.cli",
            "validate",
            "--game-dir",
            str(Path(self.out_var.get())),
        ]
        rc = self._run_cmd(cmd)
        if rc == 0:
            messagebox.showinfo("TamaCore", "Validation passed")
        else:
            messagebox.showerror("TamaCore", f"Validation failed with exit code {rc}")

    def _open_output(self) -> None:
        self._open_path(Path(self.out_var.get()))

    def _open_exports(self) -> None:
        self._open_path(Path(self.export_var.get()))

    def _open_path(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        try:
            if sys.platform.startswith("win"):
                subprocess.Popen(["explorer", str(path)])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except Exception as exc:
            messagebox.showerror("Open path failed", str(exc))


if __name__ == "__main__":
    app = App()
    app.mainloop()
