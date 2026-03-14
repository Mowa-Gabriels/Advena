


import io
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ── Palette (matches app navy/gold theme) ─────────────────────────────────────

NAVY       = colors.HexColor("#0D1526")
GOLD       = colors.HexColor("#C9A84C")
LIGHT_GOLD = colors.HexColor("#E6C76B")
CREAM      = colors.HexColor("#E8E4D9")
MUTED      = colors.HexColor("#8A9BBE")
WHITE      = colors.white
RULE       = colors.HexColor("#1E2A42")
GREEN      = colors.HexColor("#22C55E")
ROW_ODD    = colors.HexColor("#111927")
ROW_EVEN   = colors.HexColor("#0D1526")

# ── Styles ────────────────────────────────────────────────────────────────────

def _build_styles():
    base = getSampleStyleSheet()

    return {
        "h1": ParagraphStyle(
            "H1", fontName="Helvetica-Bold", fontSize=22,
            textColor=CREAM, leading=28, spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            "H2", fontName="Helvetica-Bold", fontSize=15,
            textColor=GOLD, leading=20, spaceBefore=14, spaceAfter=4,
        ),
        "h3": ParagraphStyle(
            "H3", fontName="Helvetica-Bold", fontSize=11,
            textColor=LIGHT_GOLD, leading=15, spaceBefore=10, spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "Body", fontName="Helvetica", fontSize=9,
            textColor=CREAM, leading=14, spaceAfter=4,
        ),
        "blockquote": ParagraphStyle(
            "BQ", fontName="Helvetica-Oblique", fontSize=8.5,
            textColor=MUTED, leading=13, leftIndent=12,
            borderPad=6, spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "Bullet", fontName="Helvetica", fontSize=9,
            textColor=CREAM, leading=13, leftIndent=14,
            bulletIndent=4, spaceAfter=2,
        ),
        "code": ParagraphStyle(
            "Code", fontName="Courier", fontSize=8,
            textColor=GREEN, leading=12,
            backColor=colors.HexColor("#0A1020"),
            leftIndent=8, spaceAfter=4,
        ),
        "label": ParagraphStyle(
            "Label", fontName="Helvetica-Bold", fontSize=7.5,
            textColor=GOLD, leading=11, spaceAfter=2, spaceBefore=8,
        ),
        "footer": ParagraphStyle(
            "Footer", fontName="Helvetica-Oblique", fontSize=7,
            textColor=MUTED, alignment=TA_CENTER,
        ),
    }


# ── Table helpers ─────────────────────────────────────────────────────────────

def _parse_md_table(lines: list[str], styles: dict) -> Table | None:
    """Parse a markdown table block into a reportlab Table."""
    rows = []
    for line in lines:
        if re.match(r"^\s*\|[-:| ]+\|\s*$", line):
            continue                              # skip separator row
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)

    if not rows:
        return None

    # Convert header row to bold paragraphs, body rows to normal
    rl_rows = []
    for i, row in enumerate(rows):
        style = styles["body"]
        font  = "Helvetica-Bold" if i == 0 else "Helvetica"
        rl_row = [
            Paragraph(
                _inline_md(cell),
                ParagraphStyle("tc", parent=style, fontName=font,
                               fontSize=8, leading=11, textColor=CREAM),
            )
            for cell in row
        ]
        rl_rows.append(rl_row)

    col_count = max(len(r) for r in rl_rows)
    col_width  = (A4[0] - 40 * mm) / col_count

    tbl = Table(rl_rows, colWidths=[col_width] * col_count, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0),  GOLD),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  NAVY),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [ROW_ODD, ROW_EVEN]),
        ("GRID",        (0, 0), (-1, -1), 0.3, RULE),
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",(0, 0), (-1, -1), 5),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0,0), (-1, -1), 4),
    ]))
    return tbl


def _inline_md(text: str) -> str:
    """Convert inline **bold** and *italic* to reportlab XML tags."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*",     r"<i>\1</i>", text)
    text = re.sub(r"`(.+?)`",        r"<font name='Courier'>\1</font>", text)
    # Escape bare & and < that aren't already tags
    text = re.sub(r"&(?!amp;|lt;|gt;|#)", "&amp;", text)
    return text


# ── Page background callback ──────────────────────────────────────────────────

def _dark_background(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)

    # Gold top bar
    canvas.setFillColor(GOLD)
    canvas.rect(0, A4[1] - 8 * mm, A4[0], 8 * mm, fill=1, stroke=0)

    # Footer text
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7)
    canvas.drawCentredString(
        A4[0] / 2,
        10,
        f"Advena  •  Page {doc.page}  •  For informational purposes only",
    )
    canvas.restoreState()


# ── Main converter ────────────────────────────────────────────────────────────

def markdown_to_pdf(md_text: str) -> bytes:
    """
    Convert a Markdown string to a styled PDF.
    Returns raw PDF bytes ready for st.download_button.
    """
    styles  = _build_styles()
    buf     = io.BytesIO()
    doc     = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=18 * mm,  bottomMargin=18 * mm,
    )

    story: list = []

    lines      = md_text.splitlines()
    i          = 0
    in_table   = False
    table_buf  = []

    def flush_table():
        nonlocal in_table, table_buf
        if table_buf:
            tbl = _parse_md_table(table_buf, styles)
            if tbl:
                story.append(Spacer(1, 3 * mm))
                story.append(tbl)
                story.append(Spacer(1, 3 * mm))
        table_buf = []
        in_table  = False

    while i < len(lines):
        line = lines[i]

        # ── Markdown table detection ──────────────────────────────────
        if re.match(r"^\s*\|", line):
            in_table = True
            table_buf.append(line)
            i += 1
            continue
        elif in_table:
            flush_table()

        stripped = line.strip()

        # ── Blank line ────────────────────────────────────────────────
        if not stripped:
            story.append(Spacer(1, 3 * mm))
            i += 1
            continue

        # ── HR divider ────────────────────────────────────────────────
        if re.match(r"^-{3,}$", stripped):
            story.append(Spacer(1, 2 * mm))
            story.append(HRFlowable(width="100%", thickness=0.5,
                                    color=GOLD, spaceAfter=2 * mm))
            i += 1
            continue

        # ── Code block ────────────────────────────────────────────────
        if stripped.startswith("```"):
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            story.append(Paragraph("<br/>".join(code_lines) or " ", styles["code"]))
            i += 1
            continue

        # ── Headings ──────────────────────────────────────────────────
        if stripped.startswith("### "):
            story.append(Paragraph(_inline_md(stripped[4:]), styles["h3"]))
            i += 1
            continue
        if stripped.startswith("## "):
            story.append(Spacer(1, 2 * mm))
            story.append(HRFlowable(width="100%", thickness=0.3,
                                    color=RULE, spaceBefore=1 * mm))
            story.append(Paragraph(_inline_md(stripped[3:]), styles["h2"]))
            i += 1
            continue
        if stripped.startswith("# "):
            story.append(Paragraph(_inline_md(stripped[2:]), styles["h1"]))
            story.append(HRFlowable(width="100%", thickness=1,
                                    color=GOLD, spaceAfter=4 * mm))
            i += 1
            continue

        # ── Blockquote ────────────────────────────────────────────────
        if stripped.startswith(">"):
            text = re.sub(r"^>\s*", "", stripped)
            story.append(Paragraph(_inline_md(text), styles["blockquote"]))
            i += 1
            continue

        # ── Bullet / list item ────────────────────────────────────────
        if re.match(r"^[-*+]\s", stripped):
            text = stripped[2:]
            story.append(Paragraph(f"• {_inline_md(text)}", styles["bullet"]))
            i += 1
            continue
        if re.match(r"^\d+\.\s", stripped):
            text = re.sub(r"^\d+\.\s", "", stripped)
            story.append(Paragraph(f"• {_inline_md(text)}", styles["bullet"]))
            i += 1
            continue

        # ── Normal paragraph ──────────────────────────────────────────
        story.append(Paragraph(_inline_md(stripped), styles["body"]))
        i += 1

    # Flush any trailing table
    if in_table:
        flush_table()

    doc.build(story, onFirstPage=_dark_background, onLaterPages=_dark_background)
    return buf.getvalue()
