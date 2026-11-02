"""Build writing-sheets.pdf from ground-truth/pages.txt.

Run: uv run --with reportlab python scripts/make_writing_pdf.py
Fonts: DejaVu (Ubuntu path /usr/share/fonts/truetype/dejavu/).
"""
import re
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
pdfmetrics.registerFont(TTFont("Sans", FONT_DIR / "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("SansB", FONT_DIR / "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Mono", FONT_DIR / "DejaVuSansMono.ttf"))

GREY = HexColor("#888888")
BLACK = HexColor("#000000")
W, H = A4
M = 18 * mm


def load_pages():
    text = (ROOT / "ground-truth/pages.txt").read_text()
    parts = re.split(r"^=== (P\d+) ===$", text, flags=re.M)[1:]
    return [(parts[i], parts[i + 1].strip().splitlines()) for i in range(0, len(parts), 2)]


def paper_for(code):
    # Round 1: odd pages unruled, even pages ruled. Round 2 swaps.
    n = int(code[1:])
    r1 = "UNRULED" if n % 2 else "RULED"
    r2 = "RULED" if n % 2 else "UNRULED"
    return r1, r2


INSTRUCTIONS = [
    ("SansB", 20, "Handwriting collection: how to write the pages"),
    ("Sans", 10, "github.com/danielrosehill/Daniel-Handwriting-Recognition"),
    None,
    ("SansB", 12, "Paper"),
    ("Sans", 10.5, "- Any size from A6 (pocket notepad) to A4. A5 is ideal. Mixing sizes is good."),
    ("Sans", 10.5, "- Each sheet says RULED or UNRULED for round 1. Round 2 (optional) = same text, other type."),
    ("Sans", 10.5, "- Ruled: if the rule gap is 8 mm or more, write on every line. If narrower, skip a line."),
    ("Sans", 10.5, "- Unruled: leave a clear gap (about one line height) between lines."),
    ("Sans", 10.5, "- Turn small paper landscape if a line won't fit across. White/cream paper; no graph paper."),
    None,
    ("SansB", 12, "Pen"),
    ("Sans", 10.5, "- Black (dark blue OK) ballpoint 0.7-1.0 mm or gel 0.5-0.7 mm. Ideally your everyday pen."),
    ("Sans", 10.5, "- Avoid fine 0.3-0.4 mm tips (faint in photos), pencil, and felt-tips that bleed."),
    ("Sans", 10.5, "- Using a second pen for round 2 makes the model more robust."),
    None,
    ("SansB", 12, "Writing"),
    ("Sans", 10.5, "1. Write the sheet code (e.g. P07) small in the top-right corner. Round 2: P07-2."),
    ("Sans", 10.5, "2. One printed line = one handwritten line. Never wrap a line or join two."),
    ("Sans", 10.5, "3. Copy exactly: capitals, punctuation, numbers. Don't copy the grey line numbers."),
    ("Sans", 10.5, "4. Write at your normal speed and style, not your neatest."),
    ("Sans", 10.5, "5. Run out of room? Continue on a new sheet labelled P07b (first one P07a; round 2: P07-2a, P07-2b)."),
    ("Sans", 10.5, "   Lines stay whole and in order. Small paper will often need 2-3 sheets per page."),
    ("Sans", 10.5, "6. Mistake? Keep going. Just report it, e.g. \"P07 line 4: wrote 'teh'\"."),
    ("Sans", 10.5, "7. Leave about 1.5 cm margin around the edges."),
    None,
    ("SansB", 12, "Photos"),
    ("Sans", 10.5, "- One photo per sheet, phone flat above it, whole sheet in frame, no fingers on it."),
    ("Sans", 10.5, "- Daylight or even room light, no flash, dark plain background behind the paper."),
    ("Sans", 10.5, "- Upload to the Drive fe/ folder. File names don't matter; the corner code identifies them."),
]


def cover(c):
    y = H - M - 6 * mm
    for item in INSTRUCTIONS:
        if item is None:
            y -= 4 * mm
            continue
        font, size, txt = item
        c.setFont(font, size)
        c.drawString(M, y, txt)
        y -= size * 0.5 * mm + 3.2 * mm
    c.showPage()


def sheet(c, code, lines):
    r1, r2 = paper_for(code)
    c.setFillColor(BLACK)
    c.setFont("SansB", 34)
    c.drawString(M, H - M - 12 * mm, code)
    c.setFont("SansB", 13)
    c.drawRightString(W - M, H - M - 5 * mm, f"Round 1: {r1} paper")
    c.setFont("Sans", 10)
    c.setFillColor(GREY)
    c.drawRightString(W - M, H - M - 11 * mm, f"Round 2 (optional): {r2}")
    c.drawString(M, H - M - 20 * mm,
                 f"Write \"{code}\" in the top-right corner. One line below = one handwritten line.")
    y = H - M - 36 * mm
    step = (y - M - 10 * mm) / len(lines)
    for i, line in enumerate(lines, 1):
        c.setFillColor(GREY)
        c.setFont("Sans", 11)
        c.drawRightString(M + 8 * mm, y, f"{i}")
        c.setFillColor(BLACK)
        c.setFont("Mono", 15)
        c.drawString(M + 13 * mm, y, line)
        y -= step
    c.setFillColor(GREY)
    c.setFont("Sans", 9)
    c.drawCentredString(W / 2, M - 6 * mm, f"{code} - {len(lines)} lines - mistakes: keep going and report page + line")
    c.showPage()


def main():
    out = ROOT / "writing-sheets.pdf"
    c = canvas.Canvas(str(out), pagesize=A4)
    c.setTitle("Handwriting collection sheets")
    cover(c)
    for code, lines in load_pages():
        sheet(c, code, lines)
    c.save()
    print(out)


if __name__ == "__main__":
    main()
