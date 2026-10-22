"""Reading the lease: every page is read from its image by the vision model (chosen in comparisons/models/; a PDF's own
text can lose what was typed into a form, and its check boxes), and the whole lease goes into the chat's prompt.
PyMuPDF only turns each page into a picture.
"""
import base64
import json
import shutil

import pymupdf

import config
import record

READ_IMAGE = ("Transcribe this lease page exactly, word for word, in reading order. Write a checked box as [X] and "
              "an empty box as [ ]. Do not fix, summarize, or leave out anything. Output only the page's text.")


def read_image(gateway, page):
    """One page's text, read from its image by the vision model."""
    png = page.get_pixmap(dpi=200).tobytes("png")
    reply = gateway.chat.completions.create(model=config.VISION_MODEL, **config.temperature(config.READER_GATEWAY), messages=[{"role": "user", "content": [
        {"type": "text", "text": READ_IMAGE},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png).decode()}}]}])
    return reply.choices[0].message.content or ""


def read_lease(m, pdf_path):
    """Store the tenant's lease PDF in the matter and read every page from its image; returns [{"page", "text",
    "read_by"}]."""
    shutil.copy(pdf_path, record.folder(m) / "lease.pdf")
    gateway = config.client(config.READER_GATEWAY)
    pages = [{"page": number, "text": read_image(gateway, page), "read_by": "image"}
             for number, page in enumerate(pymupdf.open(pdf_path), start=1)]
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
