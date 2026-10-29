"""Check every PDF page and render representative pages for visual review."""

from pathlib import Path
import fitz
from .essentials_pdf import SECTIONS


def inspect(path, preview_dir=None):
    errors, texts, fonts, minimum = [], [], set(), 100
    with fitz.open(path) as doc:
        dense_pages = []
        for i, page in enumerate(doc):
            text = page.get_text()
            texts.append(text)
            if not text.strip():
                errors.append(f"Blank page {i + 1}")
            if abs(page.rect.width - 595.28) > 1 or abs(page.rect.height - 841.89) > 1:
                errors.append(f"Non-A4 page {i + 1}")
            spans = [
                span
                for b in page.get_text("dict")["blocks"]
                if "lines" in b
                for line in b["lines"]
                for span in line["spans"]
            ]
            if "Original excerpts" in text:
                dense_pages.append(i)
            for span in spans:
                fonts.add(span["font"])
                minimum = min(minimum, span["size"])
                x0, y0, x1, y1 = span["bbox"]
                if x0 < 55 or x1 > 540 or y0 < 15 or y1 > page.rect.height - 15:
                    errors.append(f"Text outside page content bounds: {i + 1}, {span['text'][:35]}")
                if "\ufffd" in span["text"] or "\x00" in span["text"]:
                    errors.append(f"Unsupported glyph page {i + 1}")
            footer = [s for s in spans if s["bbox"][1] > 800 and s["text"] == str(i + 1)]
            if (
                not footer
                or abs((footer[0]["bbox"][0] + footer[0]["bbox"][2]) / 2 - page.rect.width / 2) > 2
            ):
                errors.append(f"Missing/uncentred page number {i + 1}")
        all_text = "\n".join(texts)
        for section in SECTIONS:
            if section not in all_text:
                errors.append(f"Missing section {section}")
        paths = []
        if preview_dir:
            folder = Path(preview_dir)
            folder.mkdir(parents=True, exist_ok=True)
            indices = sorted(set([0, len(doc) // 2, len(doc) - 1] + dense_pages[:1]))
            for i in indices:
                file = folder / f"page-{i + 1:03}.png"
                doc[i].get_pixmap(matrix=fitz.Matrix(1.35, 1.35)).save(file)
                paths.append(str(file))
        return {
            "pages": len(doc),
            "errors": errors,
            "fonts": sorted(fonts),
            "minimum_font_size": round(minimum, 2),
            "previews": paths,
            "visual_review": "PENDING_HUMAN_OR_AGENT_IMAGE_REVIEW",
            "doi_links": sum(len(p.get_links()) for p in doc),
        }
