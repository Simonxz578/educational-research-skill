"""Check every PDF page and render representative pages for visual review."""

from pathlib import Path
import fitz
from urllib.parse import urlparse
from .essentials_pdf import SECTIONS


def inspect(path, preview_dir=None, expected_sources=None, expected_framework=None, presentation=None):
    errors, texts, fonts, minimum = [], [], set(), 100
    with fitz.open(path) as doc:
        roadmap = presentation == "roadmap" or (
            presentation is None and "RESEARCH LOGIC" in doc[0].get_text()
        )
        dense_pages = []
        framework_pages = []
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
            if "Solid links:" in text or "Solid: source-grounded links." in text:
                framework_pages.append(i)
            if (
                "Original excerpts" in text
                or "Source-informed explanation." in text
                or "Original position and reasoning." in text
                or "Author's argument." in text
            ):
                dense_pages.append(i)
            for span in spans:
                fonts.add(span["font"])
                minimum = min(minimum, span["size"])
                x0, y0, x1, y1 = span["bbox"]
                if x0 < 55 or x1 > 540 or y0 < 15 or y1 > page.rect.height - 15:
                    errors.append(f"Text outside page content bounds: {i + 1}, {span['text'][:35]}")
                if 50 < y0 < 790 and span["size"] < 9.3:
                    errors.append(
                        f"Text too small for analytical content: page {i + 1}, {span['size']:.1f} pt"
                    )
                if roadmap and span.get("color", 0) not in {0}:
                    errors.append(f"Non-black reader text page {i + 1}")
                if "\ufffd" in span["text"] or "\x00" in span["text"]:
                    errors.append(f"Unsupported glyph page {i + 1}")
            footer = [s for s in spans if s["bbox"][1] > 800 and s["text"] == str(i + 1)]
            if (
                not footer
                or abs((footer[0]["bbox"][0] + footer[0]["bbox"][2]) / 2 - page.rect.width / 2) > 2
            ):
                errors.append(f"Missing/uncentred page number {i + 1}")
        all_text = "\n".join(texts)
        roadmap = presentation == "roadmap" or (presentation is None and "RESEARCH LOGIC" in all_text)
        if roadmap:
            from .roadmap import SECTIONS as expected_sections
        else:
            expected_sections = SECTIONS
        for section in expected_sections:
            if section not in all_text:
                errors.append(f"Missing section {section}")
        links = [link for page in doc for link in page.get_links()]
        for link in links:
            if link.get("uri"):
                parsed = urlparse(link["uri"])
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    errors.append("Malformed or unsupported external hyperlink")
            elif link.get("kind") == fitz.LINK_GOTO and not 0 <= link.get("page", -1) < len(doc):
                errors.append("Broken internal page link")
        if not roadmap and "D. Theoretical / Conceptual Framework" not in all_text:
            errors.append("Missing native framework section")
        if expected_sources:
            for source_id in expected_sources:
                if source_id not in all_text:
                    errors.append(f"Missing source in PDF: {source_id}")
        if expected_framework:
            normalised = " ".join(all_text.split())
            for construct in expected_framework.constructs:
                if " ".join(construct.name.split()) not in normalised:
                    errors.append(f"Unreadable/absent framework construct: {construct.id}")
            if "Solid links:" not in all_text and "Solid: source-grounded links." not in all_text:
                errors.append("Framework diagram legend missing")
        paths = []
        if preview_dir:
            folder = Path(preview_dir)
            folder.mkdir(parents=True, exist_ok=True)
            indices = sorted(
                set([0, len(doc) // 2, len(doc) - 1] + dense_pages[:1] + framework_pages[:1])
            )
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
            "link_validation": {
                "status": "SYNTAX_AND_INTERNAL_DESTINATIONS_CHECKED",
                "external_resolution": "NOT_CHECKED_OFFLINE",
                "total": len(links),
            },
            "doi_links": sum(len(p.get_links()) for p in doc),
        }
