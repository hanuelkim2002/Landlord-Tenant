"""Add one opinion to cases/ from a reporter PDF (a Southern Reporter page image with a text layer), for an
opinion the Westlaw print could not give as plain text. Only the court's opinion is kept; an appendix is
left out when its changes are marked by formatting (struck and underlined words), which plain text loses.

    python dev/build_case_pdf.py 50_So3d_503 "/path/to/50_So.3d_503.pdf"

Each opinion it can build is listed in OPINIONS with what the PDF needs: where the opinion stops, where the
attorneys' paragraph starts, and where the opinion's text starts. The running heads ("504 Fla. 50 SOUTHERN
REPORTER", "Cite as ...") are dropped, a star page (*504) marks each new reporter page, and the labels the
Westlaw-built files carry ("Attorneys and Law Firms", "Opinion", "All Citations") are added so every file in
cases/ has the same shape. Hyphens between two lowercase letters are removed: in the opinions listed, each
one is a hyphen at a line break (the PDF's text layer keeps them inside the word, "Su-preme"); the real
compounds in these opinions use dashes ("Multi–Family"). Spaces lost where the PDF joins lines ("outlegal")
are left as they are; quote checks ignore spaces.
"""
import re
import sys
from pathlib import Path

import PyPDF2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # so config imports from dev/
from config import CASES

OPINIONS = {
    "50_So3d_503": {"cite": "50 So.3d 503", "first_page": 503, "stop": "APPENDIX",
                    "attorneys": "John F. Harkness", "opinion": "PER CURIAM."},
}
RUNNING_HEAD = re.compile(r"^(\d{2,4} Fla\.|Cite as )")


def opinion_text(pdf, spec):
    """The opinion from the PDF, page by page, until the stop line."""
    pages = []
    for n, page in enumerate(PyPDF2.PdfReader(pdf).pages):
        lines = [l.rstrip() for l in (page.extract_text() or "").split("\n")]
        lines = [l for l in lines if not RUNNING_HEAD.match(l.strip())]
        text = "\n".join(lines).strip()
        if n:
            text = f"*{spec['first_page'] + n} " + text
        if spec["stop"] in lines:
            pages.append(text[:text.index("\n" + spec["stop"])])
            break
        pages.append(text)
    text = "\n".join(pages)
    return re.sub(r"(?<=[a-z])-\n?(?=[a-z])", "", text)     # line-break hyphens, inside a word or at a line end


def build(key, pdf):
    spec = OPINIONS[key]
    text = opinion_text(pdf, spec)
    for label, start in (("Attorneys and Law Firms", spec["attorneys"]), ("Opinion", spec["opinion"])):
        if text.count(start) < 1:
            raise ValueError(f"{key}: {start!r} not found in the PDF's text")
        at = text.index(start)
        text = text[:at] + label + "\n" + text[at:]
    return f"{spec['cite']}\n{text.strip()}\nAll Citations\n{spec['cite']}\n"


if __name__ == "__main__":
    key, pdf = sys.argv[1], sys.argv[2]
    (CASES / f"{key}.txt").write_text(build(key, pdf))
    print(f"wrote {CASES / (key + '.txt')}")
