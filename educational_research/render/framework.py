"""Editable conceptual diagram, shared by native PDF and SVG output."""

import html
import math
from reportlab.graphics.shapes import Drawing, Rect, Line, String, Polygon
from reportlab.lib import colors


def diagram_spec(framework):
    return {
        "nodes": [{"id": c.id, "label": c.name} for c in framework.constructs] if framework else [],
        "links": [r.model_dump() for r in framework.relationships] if framework else [],
        "legend": "Solid: source-verified relationship. Dashed: hypothesis/sensitising link. Arrows do not establish causality.",
    }


def drawing(framework, width):
    spec = diagram_spec(framework)
    nodes = spec["nodes"]
    if not nodes:
        d = Drawing(width, 45)
        d.add(String(5, 22, "Framework not established", fontName="ResearchSerif", fontSize=10))
        return d
    # Two columns and expandable rows retain readable labels; never shrink diagram text.
    cols = min(2, len(nodes))
    rows = math.ceil(len(nodes) / cols)
    height = rows * 88 + 28
    if height > 620:
        raise ValueError("Framework diagram too dense: simplify the explanatory model before rendering")
    d = Drawing(width, height)
    positions = {}
    cell = width / cols
    for i, n in enumerate(nodes):
        x = (i % cols) * cell + 9
        y = height - ((i // cols) + 1) * 88 + 12
        positions[n["id"]] = (x, y, cell - 30, 55)
    for link in spec["links"]:
        if link["source"] not in positions or link["target"] not in positions:
            continue
        a, b = positions[link["source"]], positions[link["target"]]
        x1, y1 = a[0] + a[2] / 2, a[1] + a[3] / 2
        x2, y2 = b[0] + b[2] / 2, b[1] + b[3] / 2
        line = Line(x1, y1, x2, y2, strokeColor=colors.black, strokeWidth=0.8)
        if link["status"] != "source_verified":
            line.strokeDashArray = [4, 3]
        d.add(line)
        if link["relation_type"] in {"proposed_mechanism", "causal", "feedback"} and (
            x1 != x2 or y1 != y2
        ):
            dx, dy = x2 - x1, y2 - y1
            ratio = max(abs(dx) / (b[2] / 2), abs(dy) / (b[3] / 2))
            tipx, tipy = x2 - dx / ratio, y2 - dy / ratio
            length = math.hypot(dx, dy)
            ux, uy = dx / length, dy / length
            d.add(
                Polygon(
                    [
                        tipx,
                        tipy,
                        tipx - 5 * ux + 2 * uy,
                        tipy - 5 * uy - 2 * ux,
                        tipx - 5 * ux - 2 * uy,
                        tipy - 5 * uy + 2 * ux,
                    ],
                    fillColor=colors.black,
                    strokeColor=colors.black,
                )
            )
        d.add(
            String((x1 + x2) / 2, (y1 + y2) / 2 + 6, link["id"], fontName="ResearchSerif", fontSize=9.5)
        )
    # Draw nodes over connectors; relation details follow in the alignment table.
    for n in nodes:
        x, y, w, h = positions[n["id"]]
        d.add(Rect(x, y, w, h, fillColor=colors.white, strokeColor=colors.black, strokeWidth=0.6))
        words = n["label"].split()
        lines = []
        current = ""
        from reportlab.pdfbase.pdfmetrics import stringWidth

        for word in words:
            candidate = (current + " " + word).strip()
            if stringWidth(candidate, "ResearchSerif", 10) > w - 12:
                if not current:
                    raise ValueError("Framework node label contains an overlong unbreakable token")
                lines.append(current)
                current = word
            else:
                current = candidate
        lines.append(current)
        if len(lines) > 3:
            raise ValueError("Framework node label exceeds readable three-line diagram limit")
        for j, line in enumerate(lines):
            d.add(String(x + 6, y + h - 16 - j * 12, line, fontName="ResearchSerif", fontSize=10))
    return d


def svg(framework):
    # Edit-friendly SVG stores labels/statuses plus vector links; PDF uses the same spec.
    spec = diagram_spec(framework)
    width = 720
    rows = math.ceil(max(1, len(spec["nodes"])) / 2)
    height = rows * 120 + 60
    positions = {n["id"]: (30 + (i % 2) * 350, 30 + (i // 2) * 120) for i, n in enumerate(spec["nodes"])}
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]
    for link in spec["links"]:
        if link["source"] in positions and link["target"] in positions:
            a, b = positions[link["source"]], positions[link["target"]]
            dash = "" if link["status"] == "source_verified" else 'stroke-dasharray="5 4"'
            out.append(
                f'<line x1="{a[0] + 145}" y1="{a[1] + 35}" x2="{b[0] + 145}" y2="{b[1] + 35}" stroke="black" {dash}/><text x="{(a[0] + b[0]) / 2 + 145}" y="{(a[1] + b[1]) / 2 + 30}" font-family="serif" font-size="13">{html.escape(link["id"])}</text>'
            )
    for n in spec["nodes"]:
        x, y = positions[n["id"]]
        out.append(
            f'<g id="{html.escape(n["id"], quote=True)}"><rect x="{x}" y="{y}" width="290" height="70" fill="white" stroke="black"/><foreignObject x="{x + 8}" y="{y + 8}" width="274" height="54"><div xmlns="http://www.w3.org/1999/xhtml" style="font:15px serif">{html.escape(n["label"])}</div></foreignObject></g>'
        )
    out.append(
        f'<text x="20" y="{height - 12}" font-family="serif" font-size="12">Solid: source-verified. Dashed: proposed/sensitising. No causal identification implied.</text></svg>'
    )
    return "\n".join(out)
