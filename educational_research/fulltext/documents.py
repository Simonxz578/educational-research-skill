"""Extract actual documents with stable native locators; scripts are never executed."""

import re
from difflib import SequenceMatcher
from html import unescape
from html.parser import HTMLParser
from xml.etree import ElementTree


def normal(text):
    return re.sub(r"\s+", " ", unescape(text)).strip()


class ArticleHTML(HTMLParser):
    """Retain headings/paragraphs/table cells; navigation cannot become evidence."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden = 0
        self.capture = []
        self.blocks = []
        self.meta = {}
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"script", "style", "nav", "footer", "form", "noscript", "aside"}:
            self.hidden += 1
        if tag == "meta":
            self.meta.setdefault(attrs.get("name", attrs.get("property", "")).lower(), []).append(
                attrs.get("content", "")
            )
        if tag == "link" and attrs.get("href"):
            self.links.append(attrs)
        if not self.hidden and tag in {
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "p",
            "td",
            "th",
            "figcaption",
        }:
            if self.capture:
                self.capture[-1][2] = True
            self.capture.append([tag, [], False])

    def handle_endtag(self, tag):
        if tag in {"script", "style", "nav", "footer", "form", "noscript", "aside"}:
            self.hidden = max(0, self.hidden - 1)
        if not self.hidden and self.capture and self.capture[-1][0] == tag:
            kind, content, nested = self.capture.pop()
            value = normal("".join(content))
            if value and not nested:
                self.blocks.append((kind, value))

    def handle_data(self, data):
        if not self.hidden:
            for _, content, _ in self.capture:
                content.append(data)


def extract(data, content_type=""):
    """Return text, exact locator records, headings, type and page count."""
    paragraphs, headings = [], []
    if data.lstrip().startswith(b"%PDF-"):
        import fitz

        with fitz.open(stream=data, filetype="pdf") as pdf:
            if pdf.needs_pass:
                raise ValueError("Encrypted PDF requires authorised local handling")
            pages = len(pdf)
            for i, page in enumerate(pdf):
                for j, block in enumerate(page.get_text("blocks"), 1):
                    value = normal(block[4])
                    if value:
                        paragraphs.append({"locator": f"PDF page {i + 1}, block {j}", "text": value})
            text = "\n\n".join(p["text"] for p in paragraphs)
            if len(text.strip()) < 300:
                raise ValueError("Scanned/empty PDF: OCR and reading remain unresolved")
            return (
                text,
                paragraphs,
                re.findall(
                    r"(?im)^.{0,10}(?:methods?|results?|discussion|references|conclusions?).{0,30}$",
                    text,
                ),
                "application/pdf",
                pages,
            )
    decoded = data.decode("utf-8", errors="replace")
    if "pdf" in content_type.lower():
        raise ValueError("Advertised PDF has no PDF signature")
    if "html" not in content_type.lower() and re.match(
        r"\s*(?:<\?xml.*?\?>\s*)?(?:<!DOCTYPE[^>]*>\s*)?<article(?:\s|>)", decoded, re.S
    ):
        root = ElementTree.fromstring(decoded)
        body = root.find("body")
        if body is None:
            raise ValueError("XML has metadata but no article body")
        for title in root.findall(".//article-title"):
            paragraphs.append(
                {"locator": "JATS article title", "text": normal("".join(title.itertext()))}
            )
        meta = root.find("front/article-meta")
        if meta is not None:
            for tag in ["contrib-group", "article-id", "pub-date"]:
                for n, entry in enumerate(meta.findall(tag), 1):
                    paragraphs.append(
                        {
                            "locator": f"JATS metadata {tag} {n}",
                            "text": normal(" ".join(entry.itertext())),
                        }
                    )
        for index, section in enumerate(body.findall(".//sec"), 1):
            heading = (
                normal("".join(section.find("title").itertext()))
                if section.find("title") is not None
                else f"Section {index}"
            )
            headings.append(heading)
            for j, p in enumerate(section.findall("./p"), 1):
                paragraphs.append(
                    {"locator": f"{heading}, paragraph {j}", "text": normal("".join(p.itertext()))}
                )
        refs = root.find("back/ref-list")
        if refs is not None:
            headings.append("References")
            paragraphs.append({"locator": "References", "text": normal(" ".join(refs.itertext()))})
        return "\n\n".join(p["text"] for p in paragraphs), paragraphs, headings, "application/xml", None
    if "<html" not in decoded.lower() and "<p" not in decoded.lower():
        raise ValueError("Resource is neither a readable PDF, article HTML nor JATS")
    parser = ArticleHTML()
    parser.feed(decoded)
    heading, index, hierarchy = "Article", 0, {}
    for tag, value in parser.blocks:
        if tag.startswith("h") and len(tag) == 2 and tag[1].isdigit():
            level = int(tag[1])
            hierarchy = {depth: name for depth, name in hierarchy.items() if depth < level}
            hierarchy[level] = value
            heading, index = (
                " / ".join(name for depth, name in sorted(hierarchy.items()) if depth > 1) or value,
                0,
            )
            headings.append(value)
        else:
            index += 1
        paragraphs.append(
            {"locator": f"{heading}, paragraph {index}" if index else heading, "text": value}
        )
    return "\n\n".join(p["text"] for p in paragraphs), paragraphs, headings, "text/html", None


def content_issues(source, text, paragraphs, headings):
    issues = []
    lower = text.casefold()
    # These identify access screens; incidental discussion of subscriptions is not a login screen.
    blockers = [
        "verify you are human",
        "complete the captcha",
        "sign in to access this article",
        "purchase access to this article",
        "access denied",
        "checking your browser",
    ]
    if any(s in lower[:6000] for s in blockers):
        issues.append("PAYWALL_OR_LOGIN_BLOCKED")

    def title_key(value):
        return re.sub(r"[^a-z0-9]", "", value.casefold())

    candidates = [
        p["text"] for p in paragraphs if p["locator"] == "JATS article title" or p["locator"] in headings
    ]
    if paragraphs and paragraphs[0]["locator"].startswith("PDF page"):
        candidates = [p["text"] for p in paragraphs[:8] if p["locator"].startswith("PDF page 1,")]
    wanted = title_key(source.title)
    title_matches = any(
        SequenceMatcher(None, wanted, title_key(value)).ratio() >= 0.90
        or (wanted in title_key(value) and len(wanted) / max(1, len(title_key(value))) >= 0.5)
        for value in candidates
    )
    if not title_matches:
        issues.append("Title/body identity mismatch")
    if (
        source.authors
        and source.authors[0].family
        and source.authors[0].family.casefold() not in lower[:12000]
    ):
        issues.append("First author not confirmed in document front matter")
    if len(re.findall(r"\b[A-Za-z]+(?:['’-][A-Za-z]+)*\b", text)) < 800 or len(paragraphs) < 6:
        issues.append("Abstract/fragment: insufficient article body")
    structure = " ".join(headings).lower()
    empirical = all(
        re.search(p, structure)
        for p in [
            r"\b(methods?|materials|procedure)\b",
            r"\b(results?|findings)\b",
            r"\b(discussion|conclusions?)\b",
            r"\breferences\b",
        ]
    )
    conceptual = all(
        re.search(p, structure)
        for p in [
            r"\bintroduction\b",
            r"\b(theory|theoretical|conceptual|argument)\b",
            r"\b(discussion|conclusions?)\b",
            r"\breferences\b",
        ]
    )
    kind = source.reading.scholarly_kind if source.reading else source.evidence_kind.lower()
    if not empirical and not (conceptual and any(k in kind for k in ["theor", "concept", "policy"])):
        issues.append("Full-text structure/completeness not established; needs manual validation")
    if source.abstract and SequenceMatcher(None, normal(source.abstract), normal(text)).ratio() > 0.8:
        issues.append("Resource repeats only the abstract")
    return issues
