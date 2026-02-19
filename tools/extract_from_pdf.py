from pathlib import Path
import fitz  # PyMuPDF

PDF = Path("input") / "TamaCore_Game_Design_WITH_IMAGES.pdf"
DROP = Path("output") / "assets_raw" / "_drop_all"

def main():
    if not PDF.exists():
        raise SystemExit(f"PDF puuttuu: {PDF}\nLaita se input/ -kansioon nimellä TamaCore_Game_Design_WITH_IMAGES.pdf")

    DROP.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(PDF)
    saved = 0

    for page_i in range(len(doc)):
        page = doc[page_i]
        for img_i, img in enumerate(page.get_images(full=True), start=1):
            xref = img[0]
            extracted = doc.extract_image(xref)
            ext = extracted.get("ext", "png")
            out = DROP / f"page_{page_i+1:02d}_img_{img_i:02d}.{ext}"
            out.write_bytes(extracted["image"])
            saved += 1

    print(f"[✓] Extracted {saved} images -> {DROP}")

if __name__ == "__main__":
    main()
