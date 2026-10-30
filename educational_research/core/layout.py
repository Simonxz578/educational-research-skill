"""Supported native presentation layouts; never resolve arbitrary user-supplied paths."""

from pathlib import Path


def audit_dir(folder):
    folder = Path(folder)
    return folder / "evidence" if (folder / "evidence" / "Execution_Receipt.json").exists() else folder


def presentation(folder):
    import json

    path = Path(folder) / "Execution_Receipt.json"
    return (
        json.loads(path.read_text()).get("presentation", "evidence-pack")
        if path.exists()
        else "evidence-pack"
    )


def reader_pdf(folder, kind=None):
    folder = Path(folder)
    return (
        folder.parent / "Research_Roadmap.pdf"
        if (kind or presentation(folder)) == "roadmap"
        else folder / "Educational_Research_Essentials.pdf"
    )
