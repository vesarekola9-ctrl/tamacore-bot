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
        self.geometry("980x760")
        self.minsize(980, 760)

        self.pack_var = tk.StringVar(value=str(ROOT / "assets" / "packs" / "demo_pack"))
        self.packs_root_var = tk.StringVar(value=str(ROOT / "assets" / "packs"))
        self.template_var = tk.StringVar(value=str(ROOT / "templates" / "gdevelop_template"))
        self.out_var = tk.StringVar(value=str((ROOT.parent / "tamacore-game").resolve()))
        self.out_root_var = tk.StringVar(value=str((ROOT / "batch_games").resolve()))
        self.export_var = tk.StringVar(value=str((ROOT / "exports").resolve()))
        self.export_root_var = tk.StringVar(value=str((ROOT / "batch_exports").resolve()))
        self.bundle_var = tk.StringVar(value=str((ROOT / "release_bundle").resolve()))
        self.bundle_root_var = tk.StringVar(value=str((ROOT / "batch_bundles").resolve()))
        self.workspace_var = tk.StringVar(value=str((ROOT / "auto_workspace").resolve()))
        self.auto_pack_var = tk.StringVar(value="auto_pack")
        self.auto_game_var = tk.StringVar(value="auto_game")

        self.v31_var = tk.BooleanVar(value=True)
        self.v32_var = tk.BooleanVar(value=True)
        self.demo_layout_var = tk.BooleanVar(value=True)
        self.export_web_var = tk.BooleanVar(value=True)
        self.export_zip_var = tk.BooleanVar(value=True)
        self.export_android_var = tk.BooleanVar(value=False)
        self.bundle_release_var = tk.BooleanVar(value=True)
        self.generate_assets_var = tk.BooleanVar(value=True)

        self._build_ui()

    def _build_ui(self) -> None:
        root_notebook = ttk.Notebook(self)
        root_notebook.pack(fill="both", expand=True, padx=10, pady=10)

        single_tab = ttk.Frame(root_notebook)
        batch_tab = ttk.Frame(root_notebook)
        auto_tab = ttk.Frame(root_notebook)
        log_tab = ttk.Frame(root_notebook)

        root_notebook.add(single_tab, text="Single")
        root_notebook.add(batch_tab, text="Batch")
        root_notebook.add(auto_tab, text="Auto")
        root_notebook.add(log_tab, text="Log")

        self._build_single_tab(single_tab)
        self._build_batch_tab(batch_tab)
        self._build_auto_tab(auto_tab)
        self._build_log_tab(log_tab)

    def _build_single_tab(self, parent: ttk.Frame) -> None:
        pad = {"padx": 8, "pady": 6}

        top = ttk.LabelFrame(parent, text="Single Game")
        top.pack(fill="x", padx=12, pady=12)

        ttk.Label(top, text="Pack").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(top, textvariable=self.pack_var, width=86).grid(row=0, column=1, sticky="ew", **pad)
        ttk.Button(top, text="Browse", command=lambda: self._browse_dir(self.pack_var)).grid(row=0, column=2, **pad)

        ttk.Label(top, text="Template").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(top, textvariable=self.template_var, width=86).grid(row=1, column=1, sticky="ew", **pad)
        ttk.Button(top, text="Browse", command=lambda: self._browse_dir(self.template_var)).grid(row=1, column=2, **pad)

        ttk.Label(top, text="Output").grid(row=2, column=0, sticky="w", **pad)
        ttk.Entry(top, textvariable=self.out_var, width=86).grid(row=2, column=1, sticky="ew", **pad)
        ttk.Button(top, text="Browse", command=lambda: self._browse_dir(self.out_var)).grid(row=2, column=2, **pad)

        ttk.Label(top, text="Exports").grid(row=3, column=0, sticky="w", **pad)
        ttk.Entry(top, textvariable=self.export_var, width=86).grid(row=3, column=1, sticky="ew", **pad)
        ttk.Button(top, text="Browse", command=lambda: self._browse_dir(self.export_var)).grid(row=3, column=2, **pad)

        ttk.Label(top, text="Bundle").grid(row=4, column=0, sticky="w", **pad)
        ttk.Entry(top, textvariable=self.bundle_var, width=86).grid(row=4, column=1, sticky="ew", **pad)
        ttk.Button(top, text="Browse", command=lambda: self._browse_dir(self.bundle_var)).grid(row=4, column=2, **pad)

        top.columnconfigure(1, weight=1)

        opts = ttk.LabelFrame(parent, text="Options")
        opts.pack(fill="x", padx=12, pady=(0, 12))

        ttk.Checkbutton(opts, text="v3.1", variable=self.v31_var).pack(anchor="w", padx=10, pady=4)
        ttk.Checkbutton(opts, text="v3.2", variable=self.v32_var).pack(anchor="w", padx=10, pady=4)
        ttk.Checkbutton(opts, text="With demo layout", variable=self.demo_layout_var).pack(anchor="w", padx=10, pady=4)
        ttk.Checkbutton(opts, text="Generate assets", variable=self.generate_assets_var).pack(anchor="w", padx=10, pady=4)
        ttk.Checkbutton(opts, text="Export Web", variable=self.export_web_var).pack(anchor="w", padx=10, pady=4)
        ttk.Checkbutton(opts, text="Export ZIP", variable=self.export_zip_var).pack(anchor="w", padx=10, pady=4)
        ttk.Checkbutton(opts, text="Export Android stub", variable=self.export_android_var).pack(anchor="w", padx=10, pady=4)
        ttk.Checkbutton(opts, text="Create Release Bundle", variable=self.bundle_release_var).pack(anchor="w", padx=10, pady=4)

        actions = ttk.Frame(parent)
        actions.pack(fill="x", padx=12, pady=(0, 12))

        ttk.Button(actions, text="Inspect Pack", command=self._inspect_pack).pack(side="left", padx=6)
        ttk.Button(actions, text="Generate Assets", command=self._generate_assets).pack(side="left", padx=6)
        ttk.Button(actions, text="Build Only", command=self._build_game).pack(side="left", padx=6)
        ttk.Button(actions, text="Make Game", command=self._make_game).pack(side="left", padx=6)
        ttk.Button(actions, text="Validate Build", command=self._validate_game).pack(side="left", padx=6)
        ttk.Button(actions, text="Validate Exports", command=self._validate_exports).pack(side="left", padx=6)

        actions2 = ttk.Frame(parent)
        actions2.pack(fill="x", padx=12, pady=(0, 12))

        ttk.Button(actions2, text="Open Output", command=lambda: self._open_path(Path(self.out_var.get()))).pack(side="left", padx=6)
        ttk.Button(actions2, text="Open Exports", command=lambda: self._open_path(Path(self.export_var.get()))).pack(side="left", padx=6)
        ttk.Button(actions2, text="Open Bundle", command=lambda: self._open_path(Path(self.bundle_var.get()))).pack(side="left", padx=6)
        ttk.Button(actions2, text="Open game.json", command=lambda: self._open_file(Path(self.out_var.get()) / "game.json")).pack(side="left", padx=6)
        ttk.Button(actions2, text="Open BUILD_REPORT", command=lambda: self._open_file(Path(self.out_var.get()) / "BUILD_REPORT.txt")).pack(side="left", padx=6)
        ttk.Button(actions2, text="Open EXPORT_REPORT", command=lambda: self._open_file(Path(self.export_var.get()) / "EXPORT_REPORT.txt")).pack(side="left", padx=6)

    def _build_batch_tab(self, parent: ttk.Frame) -> None:
        pad = {"padx": 8, "pady": 6}

        frame = ttk.LabelFrame(parent, text="Batch Factory")
        frame.pack(fill="x", padx=12, pady=12)

        ttk.Label(frame, text="Packs Root").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(frame, textvariable=self.packs_root_var, width=86).grid(row=0, column=1, sticky="ew", **pad)
        ttk.Button(frame, text="Browse", command=lambda: self._browse_dir(self.packs_root_var)).grid(row=0, column=2, **pad)

        ttk.Label(frame, text="Template").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(frame, textvariable=self.template_var, width=86).grid(row=1, column=1, sticky="ew", **pad)
        ttk.Button(frame, text="Browse", command=lambda: self._browse_dir(self.template_var)).grid(row=1, column=2, **pad)

        ttk.Label(frame, text="Out Root").grid(row=2, column=0, sticky="w", **pad)
        ttk.Entry(frame, textvariable=self.out_root_var, width=86).grid(row=2, column=1, sticky="ew", **pad)
        ttk.Button(frame, text="Browse", command=lambda: self._browse_dir(self.out_root_var)).grid(row=2, column=2, **pad)

        ttk.Label(frame, text="Export Root").grid(row=3, column=0, sticky="w", **pad)
        ttk.Entry(frame, textvariable=self.export_root_var, width=86).grid(row=3, column=1, sticky="ew", **pad)
        ttk.Button(frame, text="Browse", command=lambda: self._browse_dir(self.export_root_var)).grid(row=3, column=2, **pad)

        ttk.Label(frame, text="Bundle Root").grid(row=4, column=0, sticky="w", **pad)
        ttk.Entry(frame, textvariable=self.bundle_root_var, width=86).grid(row=4, column=1, sticky="ew", **pad)
        ttk.Button(frame, text="Browse", command=lambda: self._browse_dir(self.bundle_root_var)).grid(row=4, column=2, **pad)

        frame.columnconfigure(1, weight=1)

        opts = ttk.LabelFrame(parent, text="Batch Options")
        opts.pack(fill="x", padx=12, pady=(0, 12))

        ttk.Checkbutton(opts, text="With demo layout", variable=self.demo_layout_var).pack(anchor="w", padx=10, pady=4)
        ttk.Checkbutton(opts, text="v3.2", variable=self.v32_var).pack(anchor="w", padx=10, pady=4)
        ttk.Checkbutton(opts, text="Generate assets", variable=self.generate_assets_var).pack(anchor="w", padx=10, pady=4)
        ttk.Checkbutton(opts, text="Export Web", variable=self.export_web_var).pack(anchor="w", padx=10, pady=4)
        ttk.Checkbutton(opts, text="Export ZIP", variable=self.export_zip_var).pack(anchor="w", padx=10, pady=4)
        ttk.Checkbutton(opts, text="Create Release Bundle", variable=self.bundle_release_var).pack(anchor="w", padx=10, pady=4)

        actions = ttk.Frame(parent)
        actions.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Button(actions, text="Run Batch", command=self._make_batch).pack(side="left", padx=6)
        ttk.Button(actions, text="Open Batch Games", command=lambda: self._open_path(Path(self.out_root_var.get()))).pack(side="left", padx=6)
        ttk.Button(actions, text="Open Batch Exports", command=lambda: self._open_path(Path(self.export_root_var.get()))).pack(side="left", padx=6)
        ttk.Button(actions, text="Open Batch Bundles", command=lambda: self._open_path(Path(self.bundle_root_var.get()))).pack(side="left", padx=6)
        ttk.Button(actions, text="Open BATCH_REPORT", command=lambda: self._open_file(Path(self.out_root_var.get()) / "BATCH_REPORT.json")).pack(side="left", padx=6)

    def _build_auto_tab(self, parent: ttk.Frame) -> None:
        pad = {"padx": 8, "pady": 6}

        frame = ttk.LabelFrame(parent, text="Auto Mode")
        frame.pack(fill="x", padx=12, pady=12)

        ttk.Label(frame, text="Workspace").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(frame, textvariable=self.workspace_var, width=86).grid(row=0, column=1, sticky="ew", **pad)
        ttk.Button(frame, text="Browse", command=lambda: self._browse_dir(self.workspace_var)).grid(row=0, column=2, **pad)

        ttk.Label(frame, text="Template").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(frame, textvariable=self.template_var, width=86).grid(row=1, column=1, sticky="ew", **pad)
        ttk.Button(frame, text="Browse", command=lambda: self._browse_dir(self.template_var)).grid(row=1, column=2, **pad)

        ttk.Label(frame, text="Auto Pack").grid(row=2, column=0, sticky="w", **pad)
        ttk.Entry(frame, textvariable=self.auto_pack_var, width=40).grid(row=2, column=1, sticky="w", **pad)

        ttk.Label(frame, text="Auto Game").grid(row=3, column=0, sticky="w", **pad)
        ttk.Entry(frame, textvariable=self.auto_game_var, width=40).grid(row=3, column=1, sticky="w", **pad)

        frame.columnconfigure(1, weight=1)

        actions = ttk.Frame(parent)
        actions.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Button(actions, text="Run Auto", command=self._run_auto).pack(side="left", padx=6)
        ttk.Button(actions, text="Open Workspace", command=lambda: self._open_path(Path(self.workspace_var.get()))).pack(side="left", padx=6)
        ttk.Button(actions, text="Open Auto Games", command=lambda: self._open_path(Path(self.workspace_var.get()) / "games")).pack(side="left", padx=6)
        ttk.Button(actions, text="Open Auto Exports", command=lambda: self._open_path(Path(self.workspace_var.get()) / "exports")).pack(side="left", padx=6)
        ttk.Button(actions, text="Open Auto Bundles", command=lambda: self._open_path(Path(self.workspace_var.get()) / "bundles")).pack(side="left", padx=6)

    def _build_log_tab(self, parent: ttk.Frame) -> None:
        log_frame = ttk.LabelFrame(parent, text="Log")
        log_frame.pack(fill="both", expand=True, padx=12, pady=12)

        self.log = tk.Text(log_frame, wrap="word", height=28)
        self.log.pack(fill="both", expand=True, padx=8, pady=8)

    def _browse_dir(self, var: tk.StringVar) -> None:
        path = filedialog.askdirectory(initialdir=var.get() or str(ROOT))
        if path:
            var.set(path)

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
        rc = self._run_cmd([
            sys.executable, "-m", "tamacore.cli", "inspect-pack",
            "--pack", str(Path(self.pack_var.get()))
        ])
        if rc == 0:
            messagebox.showinfo("TamaCore", "Pack inspection passed")
        else:
            messagebox.showerror("TamaCore", f"Pack inspection failed with exit code {rc}")

    def _generate_assets(self) -> None:
        rc = self._run_cmd([
            sys.executable, "-m", "tamacore.cli", "generate-assets",
            "--pack", str(Path(self.pack_var.get()))
        ])
        if rc == 0:
            messagebox.showinfo("TamaCore", "Assets generated")
        else:
            messagebox.showerror("TamaCore", f"Asset generation failed with exit code {rc}")

    def _build_game(self) -> None:
        cmd = [
            sys.executable, "-m", "tamacore.cli", "build",
            "--pack", str(Path(self.pack_var.get())),
            "--template", str(Path(self.template_var.get())),
            "--out", str(Path(self.out_var.get())),
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
            sys.executable, "-m", "tamacore.cli", "make-game",
            "--pack", str(Path(self.pack_var.get())),
            "--template", str(Path(self.template_var.get())),
            "--out", str(Path(self.out_var.get())),
            "--export-out", str(Path(self.export_var.get())),
        ]
        if self.demo_layout_var.get():
            cmd.append("--with-demo-layout")
        if self.v31_var.get():
            cmd.append("--v31")
        if self.v32_var.get():
            cmd.append("--v32")
        if self.generate_assets_var.get():
            cmd.append("--generate-assets")
        if self.export_web_var.get():
            cmd.append("--export-web")
        if self.export_zip_var.get():
            cmd.append("--export-zip")
        if self.export_android_var.get():
            cmd.append("--export-android")
        if self.bundle_release_var.get():
            cmd.extend(["--bundle-release", "--bundle-out", str(Path(self.bundle_var.get()))])

        rc = self._run_cmd(cmd)
        if rc == 0:
            messagebox.showinfo("TamaCore", "Make Game completed")
        else:
            messagebox.showerror("TamaCore", f"Make Game failed with exit code {rc}")

    def _make_batch(self) -> None:
        cmd = [
            sys.executable, "-m", "tamacore.cli", "make-batch",
            "--packs-root", str(Path(self.packs_root_var.get())),
            "--template", str(Path(self.template_var.get())),
            "--out-root", str(Path(self.out_root_var.get())),
            "--export-root", str(Path(self.export_root_var.get())),
            "--bundle-root", str(Path(self.bundle_root_var.get())),
        ]
        if self.demo_layout_var.get():
            cmd.append("--with-demo-layout")
        if self.v32_var.get():
            cmd.append("--v32")
        if self.generate_assets_var.get():
            cmd.append("--generate-assets")
        if self.export_web_var.get():
            cmd.append("--export-web")
        if self.export_zip_var.get():
            cmd.append("--export-zip")
        if self.bundle_release_var.get():
            cmd.append("--bundle-release")

        rc = self._run_cmd(cmd)
        if rc == 0:
            messagebox.showinfo("TamaCore", "Batch completed")
        else:
            messagebox.showerror("TamaCore", f"Batch failed with exit code {rc}")

    def _run_auto(self) -> None:
        cmd = [
            sys.executable, "-m", "tamacore.cli", "auto",
            "--workspace", str(Path(self.workspace_var.get())),
            "--template", str(Path(self.template_var.get())),
            "--pack-name", self.auto_pack_var.get(),
            "--game-name", self.auto_game_var.get(),
        ]
        rc = self._run_cmd(cmd)
        if rc == 0:
            messagebox.showinfo("TamaCore", "Auto mode completed")
        else:
            messagebox.showerror("TamaCore", f"Auto mode failed with exit code {rc}")

    def _validate_game(self) -> None:
        rc = self._run_cmd([
            sys.executable, "-m", "tamacore.cli", "validate",
            "--game-dir", str(Path(self.out_var.get()))
        ])
        if rc == 0:
            messagebox.showinfo("TamaCore", "Build validation passed")
        else:
            messagebox.showerror("TamaCore", f"Build validation failed with exit code {rc}")

    def _validate_exports(self) -> None:
        rc = self._run_cmd([
            sys.executable, "-m", "tamacore.cli", "validate-exports",
            "--export-dir", str(Path(self.export_var.get()))
        ])
        if rc == 0:
            messagebox.showinfo("TamaCore", "Export validation passed")
        else:
            messagebox.showerror("TamaCore", f"Export validation failed with exit code {rc}")

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

    def _open_file(self, path: Path) -> None:
        if not path.exists():
            messagebox.showwarning("Missing file", f"Not found: {path}")
            return
        try:
            if sys.platform.startswith("win"):
                subprocess.Popen(["cmd", "/c", "start", "", str(path)])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except Exception as exc:
            messagebox.showerror("Open file failed", str(exc))


if __name__ == "__main__":
    app = App()
    app.mainloop()
