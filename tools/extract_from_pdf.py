from pathlib import Path
import fitz  # PyMuPDF

def ensure_dirs(base: Path):
    (base / "pages").mkdir(parents=True, exist_ok=True)
    (base / "embedded").mkdir(parents=True, exist_ok=True)

def extract_pages_as_png(pdf_path: Path, out_pages: Path, zoom: float = 2.5):
    doc = fitz.open(pdf_path)
    mat = fitz.Matrix(zoom, zoom)
    for i in range(len(doc)):
        page = doc[i]
        pix = page.get_pixmap(matrix=mat, alpha=True)
        out_file = out_pages / f"page_{i+1:02d}.png"
        pix.save(str(out_file))
    doc.close()

def extract_embedded_images(pdf_path: Path, out_embedded: Path):
    doc = fitz.open(pdf_path)
    for page_index in range(len(doc)):
        page = doc[page_index]
        image_list = page.get_images(full=True)
        for img_i, img in enumerate(image_list):
            xref = img[0]
            base = doc.extract_image(xref)
            img_bytes = base["image"]
            ext = base.get("ext", "png")
            out_file = out_embedded / f"p{page_index+1:02d}_img{img_i+1:02d}.{ext}"
            with open(out_file, "wb") as f:
                f.write(img_bytes)
    doc.close()

def main():
    pdf = Path("input") / "TamaCore_Game_Design_WITH_IMAGES.pdf"
    if not pdf.exists():
        raise SystemExit(f"PDF puuttuu: {pdf}. Laita se input/ -kansioon.")

    out_root = Path("output") / "extracted"
    ensure_dirs(out_root)

    print(f"[+] Render pages -> {out_root/'pages'}")
    extract_pages_as_png(pdf, out_root / "pages", zoom=2.5)

    print(f"[+] Extract embedded -> {out_root/'embedded'}")
    extract_embedded_images(pdf, out_root / "embedded")

    print("[✓] Done.")

if __name__ == "__main__":
    main()
