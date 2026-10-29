"""Native local PDF extraction; PDF and printed-page locators remain separate."""

from pathlib import Path
import hashlib
import fitz
from ..models import Segment


def read_pdf(path, source_url=None, licence="user supplied; rights not independently verified"):
    path = Path(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    segments = []
    with fitz.open(path) as doc:
        for i, page in enumerate(doc, 1):
            text = page.get_text()
            if text.strip():
                segments.append(
                    Segment(
                        id=f"pdf-{i}",
                        text=text,
                        url=source_url or f"urn:sha256:{digest}",
                        locator=f"PDF page {i}; printed page unknown",
                        pdf_page=i,
                        licence=licence,
                    )
                )
    if not segments:
        raise ValueError("No native PDF text: scanned/OCR source requires explicit OCR and validation")
    return segments
