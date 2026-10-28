"""v1's lease intake, run unedited, for the speed test: the PDF's own text (PyPDF2), then Gemma on UF copies four
clauses into the lease profile. Run by speed.py with a Python that has v1's packages, since v1 and v2 both have
modules named config and lease. Usage: python v1_intake.py LEASE.pdf OUT.json
"""
import contextlib
import io
import json
import sys
import tempfile
import time
from pathlib import Path

V1 = Path(__file__).resolve().parents[3] / "v1"
sys.path.insert(0, str(V1))
import lease  # noqa: E402  (v1's lease.py, found through the line above)


def main():
    """Time v1's two intake steps on one lease and write what it read."""
    pdf, out = sys.argv[1], Path(sys.argv[2])
    error = ""
    with tempfile.TemporaryDirectory() as matter, contextlib.redirect_stdout(io.StringIO()):   # v1 prints each page
        start = time.perf_counter()
        pages = lease.ingest_pdf(pdf, Path(matter))
        try:
            lease.extract_profile(pages)
        except Exception as problem:                     # keep the time even if Gemma's profile does not parse
            error = f"{type(problem).__name__}: {problem}"[:300]
        seconds = time.perf_counter() - start
    out.write_text(json.dumps({"seconds": round(seconds, 1), "error": error,
                               "pages": [{"page": p["page"], "text": p["text"]} for p in pages]}))


if __name__ == "__main__":
    main()
