"""Apply agent-reviewed extraction only through validated input records."""

import json
from pathlib import Path
from ..models import Source
from .pdf_reader import read_pdf


def load(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = data.get("sources", []) if isinstance(data, dict) else data
    sources = [Source.model_validate(row) for row in rows]
    if len({s.id.casefold() for s in sources}) != len(sources):
        raise ValueError("Source IDs must be unique before deduplication")
    return sources


def attach_pdf(source, path):
    data = source.model_dump()
    data["segments"] += [s.model_dump() for s in read_pdf(path, source.url or None)]
    data["access"] = "USER_SUPPLIED"
    return Source.model_validate(data)
