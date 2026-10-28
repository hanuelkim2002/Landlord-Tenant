"""Reading the lease: every page is read from its image by the vision model (chosen in comparisons/models/; a PDF's own
text can lose what was typed into a form, and its check boxes), and the whole lease goes into the chat's prompt.
PyMuPDF only turns each page into a picture. The pages are read 16 at a time.
"""
import base64
import json
import shutil
from concurrent.futures import ThreadPoolExecutor

import pymupdf

import config
import record

READ_IMAGE = ("Transcribe this lease page exactly, word for word, in reading order. Write a checked box as [X] and "
              "an empty box as [ ]. Do not fix, summarize, or leave out anything. Output only the page's text.")
# Each page takes the model about 3 seconds; reading 16 at once, a 46-page lease took 10 seconds against 132 one at a
# time, with every word and check box still right and no page turned away (comparisons/intake/, 2026-10-27). If
# Anthropic starts turning pages away (too many requests a minute), lower this number.
PAGES_AT_ONCE = 16


def read_image(gateway, page):
    """One page's text, read from its image by the vision model."""
    png = page.get_pixmap(dpi=200).tobytes("png")
    reply = gateway.chat.completions.create(model=config.VISION_MODEL, **config.temperature(config.READER_GATEWAY), messages=[{"role": "user", "content": [
        {"type": "text", "text": READ_IMAGE},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png).decode()}}]}])
    return reply.choices[0].message.content or ""


def read_page(gateway, pdf_path, number):
    """One page of the PDF read from its image. Each page opens its own copy of the PDF, since PyMuPDF is not built
    for threads; Python lets one thread into PyMuPDF at a time, so only the waits for the model overlap."""
    return read_image(gateway, pymupdf.open(pdf_path)[number - 1])


def read_lease(m, pdf_path):
    """Store the tenant's lease PDF in the matter and read every page from its image, PAGES_AT_ONCE at a time;
    returns [{"page", "text", "read_by"}]."""
    shutil.copy(pdf_path, record.folder(m) / "lease.pdf")
    gateway = config.client(config.READER_GATEWAY)
    numbers = range(1, pymupdf.open(pdf_path).page_count + 1)
    with ThreadPoolExecutor(PAGES_AT_ONCE) as pool:           # map gives the texts back in page order
        texts = list(pool.map(lambda number: read_page(gateway, pdf_path, number), numbers))
    pages = [{"page": number, "text": text, "read_by": "image"} for number, text in zip(numbers, texts)]
    (record.folder(m) / "lease_pages.json").write_text(json.dumps(pages, indent=1))
    record.log(m, "lease_read", pages=len(pages), from_images=sum(p["read_by"] == "image" for p in pages))
    return pages


def lease_pages(m):
    """The lease as the tool read it, page by page (empty if the matter has no lease yet)."""
    path = record.folder(m) / "lease_pages.json"
    return json.loads(path.read_text()) if path.exists() else []


def lease_text(pages):
    """The whole lease for the prompt, with a marker where each page starts."""
    return "\n\n".join(f"=== Page {p['page']} ===\n{p['text'].strip()}" for p in pages)
