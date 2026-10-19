"""Builds the test leases in leases/ from the texts in sources/.
Two are plain PDFs. One is saved as page images with no text, like a scan. One looks normal but its text cannot be
read out, like the 57-page lease v1 failed on. Run from this folder: python make_leases.py
"""
import random
import re
from pathlib import Path

import pymupdf
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFilter
from pypdf import PdfReader, PdfWriter

HERE = Path(__file__).resolve().parent
SOURCES = HERE / "sources"
OUT = HERE / "leases"
UNICODE_FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"   # has the check box marks ☒ and ☐

# How each lease looks. "kind" says what happens after the plain PDF is made.
LEASES = {
    "short_headings": dict(font="Helvetica", size=11, line=5.6, kind="text",
                           footer="Room Rental Agreement, 1419 NW 5th Avenue    Page {page} of {nb}"),
    "long_numbered": dict(font="Times", size=12, line=6.4, kind="text",
                          header="Archer Commons Student Residences | Individual Lease Agreement",
                          footer="Page {page} of {nb}        Resident's Initials: ______"),
    "scanned": dict(font="Times", size=11.5, line=5.8, kind="scan",
                    footer="Page {page} of {nb}        Tenant initials: ______  ______"),
    "broken_text": dict(font="unicode", size=10.5, line=5.4, kind="broken",
                        footer="Brightwater Flats Apartment Lease    Page {page} of {nb}"),
}

# A numbered clause whose number and caption are printed in bold, like "4.2. Due Date." or "A-2.1. Overnight Guests."
RUN_IN = re.compile(r"^((?:[A-Z]-)?\d+(?:\.\d+)*\.\s+[A-Z][^.]{0,60}\.)\s")


def source_lines(name):
    """The lines of a lease's source text. The long lease is kept in several files, read in order."""
    path = SOURCES / name
    files = sorted(path.glob("*.txt")) if path.is_dir() else [SOURCES / f"{name}.txt"]
    return "\n".join(f.read_text() for f in files).splitlines()


def plain_text(name):
    """The lease's words with the layout marks taken out: what a perfect reader would get from the PDF."""
    words = []
    for line in source_lines(name):
        if line.strip() == "<<page>>":
            continue
        if line.startswith("|"):
            line = " ".join(cell.strip() for cell in line.strip("|").split("|"))
        words.append(line.lstrip("# "))
    return "\n".join(words)


class LeasePDF(FPDF):
    """An FPDF page with the lease's running header and footer, as real leases have."""

    def __init__(self, style):
        super().__init__(format="Letter")
        self.style = style
        self.set_margins(25, 22, 25)
        self.set_auto_page_break(True, margin=22)
        if style["font"] == "unicode":
            self.add_font("unicode", "", UNICODE_FONT)
            self.add_font("unicode", "B", UNICODE_FONT)   # Arial Unicode has no bold file; bold looks the same

    def header(self):
        if self.style.get("header"):
            self.set_font(self.style["font"], "", 8.5)
            self.cell(0, 6, self.style["header"], align="C")
            self.ln(9)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.style["font"], "", 8.5)
        self.cell(0, 6, self.style["footer"].format(page=self.page_no(), nb="{nb}"), align="C")


def write_table(pdf, rows):
    """A table of rows like "| a | b |", the first row as its header."""
    cells = [[cell.strip() for cell in row.strip("|").split("|")] for row in rows]
    with pdf.table(text_align="LEFT", line_height=pdf.style["line"] * 0.9, padding=1) as table:
        for row in cells:
            table_row = table.row()
            for cell in row:
                table_row.cell(cell)
    pdf.ln(3)


def write_pdf(name, path):
    """Lay the source text out as a plain PDF: titles, headings, clauses, tables, and page breaks."""
    style = LEASES[name]
    pdf = LeasePDF(style)
    pdf.add_page()
    font, size, line = style["font"], style["size"], style["line"]
    lines = source_lines(name)
    i = 0
    while i < len(lines):
        text = lines[i]
        if text.strip() == "<<page>>":
            pdf.add_page()
        elif text.startswith("# "):
            pdf.set_font(font, "B", size + 3)
            pdf.multi_cell(0, line + 1, text[2:], align="C", new_x="LMARGIN", new_y="NEXT")
        elif text.startswith("## "):
            pdf.ln(2)
            pdf.set_font(font, "B", size)
            pdf.multi_cell(0, line, text[3:], new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        elif text.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i])
                i += 1
            pdf.set_font(font, "", size - 1.5)
            write_table(pdf, rows)
            continue
        elif text.strip():
            pdf.set_font(font, "", size)
            match = RUN_IN.match(text)
            if match and "__" not in text and "--" not in text:
                bold_caption = f"**{match.group(1)}**{text[match.end(1):]}"
                pdf.multi_cell(0, line, bold_caption, markdown=True, new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.multi_cell(0, line, text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1.5)
        i += 1
    pdf.output(str(path))


def remove_text_layer_map(path):
    """Delete each font's ToUnicode map, the table a reader uses to turn the printed letters back into text.
    The page looks the same on screen, but a reader gets nonsense or nothing: v1's failure on a real lease."""
    writer = PdfWriter(clone_from=PdfReader(path))
    for page in writer.pages:
        fonts = page["/Resources"]["/Font"]
        for key in fonts:
            font = fonts[key].get_object()
            if "/ToUnicode" in font:
                del font["/ToUnicode"]
    writer.write(path)


def scan_pages(path, seed):
    """Turn each page into a slightly tilted, speckled gray image, as a scanner would, and save only the images."""
    rng = random.Random(seed)            # the same "scan" every time the script runs
    pages = []
    for page in pymupdf.open(path):
        pix = page.get_pixmap(dpi=200, colorspace=pymupdf.csGRAY)
        image = Image.frombytes("L", (pix.width, pix.height), pix.samples)
        image = image.point(lambda v: int(v * 0.9) + 14)          # paper is never pure white
        draw = ImageDraw.Draw(image)
        for _ in range(500):                                    # dust and toner specks
            x, y = rng.randrange(image.width), rng.randrange(image.height)
            draw.ellipse((x, y, x + rng.randint(1, 3), y + rng.randint(1, 3)), fill=rng.randint(60, 160))
        image = image.rotate(rng.uniform(-0.8, 0.8), resample=Image.BICUBIC, fillcolor=232)
        pages.append(image.filter(ImageFilter.GaussianBlur(0.5)))
    pages[0].save(path, "PDF", save_all=True, append_images=pages[1:], resolution=200, quality=72)


def build(name):
    """Make one test lease and say how many pages it has and whether its text can be read out."""
    path = OUT / f"{name}.pdf"
    write_pdf(name, path)
    kind = LEASES[name]["kind"]
    if kind == "broken":
        remove_text_layer_map(path)
    if kind == "scan":
        scan_pages(path, seed=name)
    doc = pymupdf.open(path)
    readable = sum(len(re.findall(r"[A-Za-z]{3,}", page.get_text())) for page in doc)   # real words, not symbols
    written = len(re.findall(r"[A-Za-z]{3,}", plain_text(name)))
    print(f"{name:16} {doc.page_count:3} pages  {written:6} words written  {readable:6} read back by PyMuPDF")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for lease_name in LEASES:
        build(lease_name)
