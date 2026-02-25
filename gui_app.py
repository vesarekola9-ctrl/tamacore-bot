from __future__ import annotations

import sys
import threading
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

import run_pipeline


def open_folder(path: Path):
    try:
        path.mkdir(parents=True, exist_ok=True)
        if sys.platform.startswith("win"):
            subprocess.Popen(["explorer", str(path)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception as e:
        messagebox.showerror("Open folder failed", str(e))


def friendly_hint_from_error_text(text: str) -> str:
    t = (text or "").lower()

    # Common issues
    if "filenotfounderror" in t and "tamacore_game_design_with_images.pdf" in t:
        return (
            "PDF puuttuu.\n\n"
            "Korjaus:\n"
            "1) Valitse PDF (Choose PDF)\n"
            "2) Run Pipeline\n\n"
            "Varmista että PDF kopioituu kansioon: input/ "
            "nimellä 'TamaCore_Game_Design_WITH_IMAGES.pdf'."
        )

    if "pypdf2" in t or "pymupdf" in t or "fitz" in t:
        return (
            "PDF-kirjasto/riippuvuus puuttuu tai import failaa.\n\n"
            "Korjaus:\n"
            "1) Aja uusin EXE Latest Releasesta\n"
            "2) Jos buildaat itse: varmista requirements.txt ja että Actions/build on vihreä."
        )

    if "permissionerror" in t:
        return (
            "PermissionError: Windows estää kirjoittamisen.\n\n"
            "Korjaus:\n"
            "1) Sulje kaikki ohjelmat jotka käyttää output/ tiedostoja\n"
            "2) Kokeile ajaa EXE Desktopilta (ei Program Files)\n"
            "3) Jos output on OneDrive-kansiossa, kokeile paikallista kansiota."
        )

    if "no such file or directory" in t and ("tools" in t or "_mei" in t):
        return (
            "EXE ei löydä bundled tools/ -kansiota.\n\n"
            "Korjaus:\n"
            "1) Lataa uusin EXE Latest Releasesta\n"
            "2) Varmista että rolling-latest-release workflow on vihreä\n"
            "3) Varmista että build käyttää: --add-data \"tools;tools\""
        )

    if "atlas" in t and ("missing" in t or "not found" in t):
        return (
            "Atlas puuttuu.\n\n"
            "Korjaus:\n"
            "1) Varmista että pipeline ajaa atlas_pack.py\n"
            "2) Tarkista että output/atlas/atlas.png ja atlas.json syntyy."
        )

    if "gdevelop_pack" in t and ("not found" in t or "missing" in t):
        return (
            "GDevelop pack ei syntynyt.\n\n"
            "Korjaus:\n"
            "1) Tarkista run_log.txt mikä skripti failasi\n"
            "2) Varmista että tools/gdevelop_pack_generate.py on repossa"
        )

    # Fallback
    return (
        "Tuntematon virhe.\n\n"
        "Katso:\n"
        "- output/reports/run_log.txt\n"
        "- output/reports/template_analysis.json (jos analyzer ehti ajaa)\n\n"
        "Lähetä run_log.txt viimeiset rivit niin korjaan nopeasti."
    )


def read_tail(p: Path, max_chars: int = 40000) -> str:
    try:
        if not p.exists():
            return ""
        txt = p.read_text(encoding="utf-8", errors="ignore")
        return txt[-max_chars:]
    except Exception:
        return ""


def detect_last_failed_step(log_text: str) -> str:
    # run_pipeline logs:
    # [ts] > Running: X.py
    # [ts] [ok] X.py
    # [ts] [fail] ...
    lines = (log_text or "").splitlines()
    last_running = ""
    for line in lines:
        if "> Running:" in line:
            last_running = line.split("> Running:", 1)[1].strip()
        if "[fail]" in line:
            return last_running or "Unknown step"
    return ""


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TamaCoreBot GUI")
        self.geometry("720x520")

        self.base = run_pipeline.exe_dir()
        self.input_dir = self.base / "input"
        self.output_dir = self.base / "output"
        self.gdevelop_pack_dir = self.output_dir / "gdevelop_pack"
        self.reports_dir = self.output_dir / "reports"
        self.log_file = self.reports_dir / "run_log.txt"

        self.selected_pdf = tk.StringVar(value="(no pdf selected)")

        # --- Top row: PDF selection
        top = tk.Frame(self)
        top.pack(fill="x", padx=12, pady=10)

        tk.Label(top, text="PDF:").pack(side="left")
        tk.Entry(top, textvariable=self.selected_pdf, width=62).pack(side="left", padx=8)
        tk.Button(top, text="Choose PDF", command=self.choose_pdf).pack(side="left")

        # --- Buttons row
        mid = tk.Frame(self)
        mid.pack(fill="x", padx=12, pady=6)

        tk.Button(mid, text="Run Pipeline", command=self.run_pipeline_clicked, height=2).pack(side="left")
        tk.Button(mid, text="Open Output", command=lambda: open_folder(self.output_dir), height=2).pack(
            side="left", padx=8
        )
        tk.Button(mid, text="Open GDevelop Pack", command=self.open_gdevelop_pack, height=2).pack(
            side="left", padx=8
        )
        tk.Button(mid, text="Open Logs", command=lambda: open_folder(self.reports_dir), height=2).pack(side="left")

        # --- Status
        self.status_var = tk.StringVar(value=f"Base: {self.base}")
        tk.Label(self, textvariable=self.status_var).pack(anchor="w", padx=12, pady=(6, 0))

        # --- Log viewer
        tk.Label(self, text="Log (output/reports/run_log.txt):").pack(anchor="w", padx=12, pady=(10, 0))
        self.log_text = tk.Text(self, height=18)
        self.log_text.pack(fill="both", expand=True, padx=12, pady=8)

        self.refresh_log()

    def choose_pdf(self):
        p = filedialog.askopenfilename(
            title="Select PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if not p:
            return
        self.selected_pdf.set(p)

    def open_gdevelop_pack(self):
        # If pack not created yet, tell user what to do
        if not self.gdevelop_pack_dir.exists():
            messagebox.showinfo(
                "GDevelop pack not found",
                "GDevelop pack folder does not exist yet.\n\n"
                "Click 'Run Pipeline' first, then try again.\n\n"
                f"Expected folder:\n{self.gdevelop_pack_dir}",
            )
            return
        open_folder(self.gdevelop_pack_dir)

    def refresh_log(self):
        txt = read_tail(self.log_file)
        self.log_text.delete("1.0", "end")
        self.log_text.insert("1.0", txt)

        failed = detect_last_failed_step(txt)
        if failed:
            self.status_var.set(f"Last failure near: {failed}  |  Base: {self.base}")
        else:
            self.status_var.set(f"Base: {self.base}")

        self.after(1200, self.refresh_log)

    def run_pipeline_clicked(self):
        pdf = self.selected_pdf.get().strip()
        if pdf and pdf != "(no pdf selected)":
            # run_pipeline accepts drag-drop PDF via argv
            sys.argv = [sys.argv[0], pdf]
        else:
            sys.argv = [sys.argv[0]]

        def worker():
            try:
                run_pipeline.main()
                messagebox.showinfo("Done", "Pipeline finished ✅\n\nOpen Output / GDevelop Pack.")
            except Exception as e:
                # Read latest log tail and provide friendly hint
                tail = read_tail(self.log_file, 60000)
                last_step = detect_last_failed_step(tail)
                hint = friendly_hint_from_error_text(tail or str(e))
                msg = "Pipeline failed ❌\n\n"
                if last_step:
                    msg += f"Last step: {last_step}\n\n"
                msg += hint
                messagebox.showerror("Pipeline failed", msg)

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    App().mainloop()
