"""Conservative public-file hygiene scan; private source content is never an input."""

import re
import subprocess
from pathlib import Path


def scan():
    # Exclude ignored private/run files. No filenames from any private manuscript are needed.
    files = (
        subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"])
        .decode()
        .split("\0")
    )
    errors = []
    for name in filter(None, files):
        path = Path(name)
        if not path.is_file():
            continue
        if name in {
            "examples/roadmap-v3-10.pdf", "examples/roadmap-v3-20.pdf",
            "examples/roadmap-v042-10.pdf", "examples/roadmap-v042-20.pdf",
            "examples/roadmap-v043-10.pdf", "examples/roadmap-v043-20.pdf",
        }:
            import fitz

            with fitz.open(path) as pdf:
                text = " ".join(page.get_text() for page in pdf)
                if not all(
                    marker in text
                    for marker in [
                        "TEST ONLY - SYNTHETIC SOURCES",
                        "NOT SCHOLARLY EVIDENCE",
                        "Fictional001",
                        "example.test",
                    ]
                ):
                    errors.append(
                        f"Public PDF is not a clearly identified generated synthetic example: {name}"
                    )
                if path.stat().st_size > 2_000_000:
                    errors.append(f"Synthetic PDF exceeds public example size limit: {name}")
            continue
        if path.suffix.lower() in {".pdf", ".docx", ".mp4", ".zip", ".pem", ".key"}:
            errors.append(f"Protected/binary upload not allowed: {name}")
            continue
        if any(part in {"private", "outputs", ".cache", ".venv", ".venv312"} for part in path.parts):
            errors.append(f"Private/generated path tracked: {name}")
        text = path.read_text(encoding="utf-8")
        patterns = [
            r"gh[pousr]_[A-Za-z0-9]{20,}",
            r"-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----",
            r"/Users/[^/\s]+/(?:Downloads|Documents)/",
            r"(?i)(?:api_key|token)\s*=\s*[\"\'][A-Za-z0-9_-]{20,}",
        ]
        if any(re.search(pattern, text) for pattern in patterns):
            errors.append(f"Credential/private path pattern: {name}")
    return errors


if __name__ == "__main__":
    issues = scan()
    print(
        "\n".join(issues)
        if issues
        else "Public-file hygiene scan passed (no private source manuscript was accessed)."
    )
    raise SystemExit(bool(issues))
