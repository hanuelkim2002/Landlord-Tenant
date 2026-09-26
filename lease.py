"""Lease Intake: read the PDF, extract the profile with Gemma, check every quote against the page."""
import hashlib
import json
from pathlib import Path
from typing import Optional

import PyPDF2
from pydantic import BaseModel, Field

from config import MATTERS, extract_llm, squash


# ---- Ingest PDF: store the PDF under its hash and pull the text of each page. No model involved.

def ingest_pdf(pdf_path, matter_id):
    """Store the PDF under its hash and pull text page by page. No extraction yet."""
    matter_dir = MATTERS / matter_id
    matter_dir.mkdir(parents=True, exist_ok=True)

    pdf_bytes = Path(pdf_path).read_bytes()
    sha = hashlib.sha256(pdf_bytes).hexdigest()
    (matter_dir / f"lease_{sha[:12]}.pdf").write_bytes(pdf_bytes)

    pages = []
    reader = PyPDF2.PdfReader(pdf_path)
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append({"page": i, "text": text})
        kind = "SCAN?" if len(text.strip()) < 100 else "text"
        print(f"p{i:>3}  {len(text.strip()):>6} chars  {kind}")

    (matter_dir / "pages.json").write_text(json.dumps(pages, indent=2))
    print(f"\nsha256 {sha[:12]}  pages {len(pages)}")
    return pages


# ---- Lease Profile Shape: fifteen named clauses. Gemma must fill exactly this shape; Pydantic rejects anything else.

class Clause(BaseModel):
    """One lease provision: whether it exists, and if so the exact words,
    page, and section. Every LeaseProfile field is one of these."""
    present: bool = Field(description="False if the lease has no such provision.")
    quote: Optional[str] = Field(None, description="Exact text from the lease. Copy, do not paraphrase.")
    page: Optional[int] = None
    section: Optional[str] = Field(None, description="Section number or heading as printed.")


class LeaseProfile(BaseModel):
    """The structured profile extracted from one lease. Fifteen named slots,
    each a Clause. Filled by gemma, checked by check_quotes."""
    landlord_name_and_address: Clause
    tenant_names: Clause
    premises_address: Clause
    term_start: Clause          # date as printed, Python parses it later
    term_end: Clause
    rent: Clause                # amount as printed
    security_deposit: Clause
    deposit_deductions: Clause
    nonrefundable_fees: Clause
    move_out_requirements: Clause
    forwarding_address_requirement: Clause
    notices_to_landlord: Clause = Field(description="Where and HOW the tenant must send notices to the landlord: the address AND any sentence listing required delivery methods (hand, certified mail, email, etc.). Quote both together.")
    joint_and_several_liability: Clause
    signatures: Clause
    notice_before_vacating: Clause = Field(description="A term requiring the tenant to notify the landlord before moving out EARLY or abandoning, especially one tied to the deposit. Not the notice required before the lease's normal end date.")


# ---- Extract and Check: Gemma reads the lease into the profile; check_quotes confirms every quote word for word.

def extract_profile(pages):
    lease_text = "\n\n".join(f"=== PAGE {p['page']} ===\n{p['text']}" for p in pages)
    schema = json.dumps(LeaseProfile.model_json_schema(), indent=2)

    prompt = f"""You are extracting provisions from a residential lease.
Return ONLY a JSON object matching this schema, no prose, no markdown fences.
For each field: if the lease has no such provision, set present=false and leave the rest null.
Quotes must be copied exactly from the lease text. Never paraphrase or summarize.
Dates and dollar amounts go inside the quote exactly as printed.

SCHEMA:
{schema}

LEASE:
{lease_text}"""

    raw = extract_llm.invoke(prompt).content
    raw = raw.strip().removeprefix("```json").removesuffix("```").strip()
    return LeaseProfile.model_validate_json(raw)


def quote_found(quote, page_text, page):
    # A quote can start at the bottom of one page and finish at the top of the next,
    # with a running header in between. So: the front of the quote must end page N,
    # and the rest must appear on page N+1. Try every place to cut the quote.
    q = squash(quote)
    a, b = page_text.get(page, ""), page_text.get(page + 1, "")
    if q in a:
        return True
    for k in range(len(q) - 1, 0, -1):
        if a.endswith(q[:k].strip()) and q[k:].strip() in b:
            return True
    return False


def check_quotes(profile, pages):
    """Every quote must appear verbatim starting on the page it claims. May run onto the next page."""
    page_text = {p["page"]: squash(p["text"]) for p in pages}
    for name, clause in profile:
        if not clause.present:
            print(f"  --   {name}: not present")
            continue
        ok = quote_found(clause.quote, page_text, clause.page)
        print(f"  {'OK  ' if ok else 'FAIL'} {name}  p{clause.page}  {clause.section}")
        if not ok:
            print(f"        {clause.quote[:120]!r}")
