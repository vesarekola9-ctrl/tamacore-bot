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
        if sys.platform.startswith("win"):
            subprocess.Popen(["explorer", str(path)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception as e:
        messagebox.showerror("Open folder failed", str(e))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TamaCoreBot GUI")
        self.geometry("640x420")

        self.base = run_pipeline.exe_dir()
        self.input_dir = self.base / "input"
        self.output_dir = self.base / "output"
        self.log_file = self.output_dir / "reports" / "run_log.txt"

        self.selected_pdf = tk.StringVar(value="(no pdf selected)")

        top = tk.Frame(self)
        top.pack(fill="x", padx=12, pady=10)

        tk.Label(top, text="PDF:").pack(side="left")
        tk.Entry(top, textvariable=self.selected_pdf, width=55).pack(side="left", padx=8)

        tk.Button(top, text="Choose PDF", command=self.choose_pdf).pack(side="left")

        mid = tk.Frame(self)
        mid.pack(fill="x", padx=12, pady=6)

        tk.Button(mid, text="Run Pipeline", command=self.run_pipeline_clicked, height=2).pack(side="left")
        tk.Button(mid, text="Open Output Folder", command=lambda: open_folder(self.output_dir), height=2).pack(
            side="left", padx=8
        )
        tk.Button(mid, text="Open Input Folder", command=lambda: open_folder(self.input_dir), height=2).pack(
            side="left"
        )

        tk.Label(self, text="Log (output/reports/run_log.txt):").pack(anchor="w", padx=12, pady=(10, 0))

        self.log_text = tk.Text(self, height=14)
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

    def refresh_log(self):
        try:
            if self.log_file.exists():
                txt = self.log_file.read_text(encoding="utf-8", errors="ignore")
            else:
                txt = ""
        except Exception:
            txt = ""
        self.log_text.delete("1.0", "end")
        self.log_text.insert("1.0", txt[-20000:])  # keep last chunk
        self.after(1200, self.refresh_log)

    def run_pipeline_clicked(self):
        pdf = self.selected_pdf.get().strip()
        if pdf and pdf != "(no pdf selected)":
            # run_pipeline expects drag-drop argv paths
            sys.argv = [sys.argv[0], pdf]
        else:
            sys.argv = [sys.argv[0]]

        def worker():
            try:
                run_pipeline.main()
                messagebox.showinfo("Done", "Pipeline finished. Check output folder.")
            except Exception as e:
                messagebox.showerror("Pipeline failed", str(e))

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    App().mainloop()
