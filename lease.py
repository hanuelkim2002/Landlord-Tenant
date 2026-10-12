"""Lease Intake: read the PDF, extract the profile with Gemma, check every quote against the page."""
import hashlib
import json
import re
from pathlib import Path
from typing import Optional

import PyPDF2
from pydantic import BaseModel, Field

from config import extract_llm, squash


# ---- Ingest PDF: store the PDF under its hash and pull the text of each page. No model involved.

def ingest_pdf(pdf_path, matter_dir):
    """Store the PDF under its hash and pull text page by page. No extraction yet.
    matter_dir is the matter's folder, from record.matter_dir()."""
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
    """The structured profile extracted from one lease. Sixteen named slots,
    each a Clause. Filled by gemma, checked by check_quotes. A profile read before a slot was added holds None
    there (maintenance_and_repairs, added 2026-10-04): not read, which is not the same as not in the lease."""
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
    # Added 2026-10-04 (TODO item 76): asked "Is the AC part of my lease?", the model said the lease does not mention
    # air conditioning, from the other fifteen slots, none of which is about repairs.
    maintenance_and_repairs: Optional[Clause] = Field(None, description="Who must maintain and repair the unit, its systems, and its appliances (air conditioning, heating, plumbing, appliances), and how the tenant asks for a repair. Copy one passage exactly as printed, from its first word to its last, with any numbered heading inside it; never join separate passages or leave out words between them.")

    def clauses(self):
        """Each slot read from the lease, as (name, clause); a slot this profile was read without (None) is left
        out."""
        return [(name, clause) for name, clause in self if clause is not None]


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


# ---- The profile as the model reads it (TODO item 77): each clause in plain words with the cite to use. Given the
# profile as JSON, the model cited a clause with no section number by its field name ("(Lease notice_before_vacating)",
# "(term_end)"): most of the 17 turns with a field id in the eval of 2026-10-04.

LABELS = {
    "landlord_name_and_address": "the landlord's name and address",
    "tenant_names": "the tenants' names",
    "premises_address": "the address of the unit",
    "term_start": "the start of the term",
    "term_end": "the end of the term",
    "rent": "the rent",
    "security_deposit": "the security deposit",
    "deposit_deductions": "what the landlord may keep from the deposit, and how it is returned",
    "nonrefundable_fees": "fees that are not refunded",
    "move_out_requirements": "what the tenant must do at move-out",
    "forwarding_address_requirement": "giving a forwarding address",
    "notices_to_landlord": "where and how the tenant sends notices to the landlord",
    "joint_and_several_liability": "each tenant's liability for the whole lease",
    "signatures": "the signatures",
    "notice_before_vacating": "notice before moving out early",
    "maintenance_and_repairs": "maintenance and repairs",
}
SECTION_NUMBER = re.compile(r"^\s*(?:(article|section|paragraph)\s+)?(\d+(?:\.\d+)*)\.?(?=\s|$)", re.I)
# a lease cite as lease_cite gives it: "Lease Section 4.3", "Lease Article 7", "Lease, page 1", with any space between
# the words: the model wrote "Lease Section 7.2", a narrow no-break space, and the program printed nothing under
# the reply (eval of 2026-10-04, TODO item 85). Here since 2026-10-11, for the letter's check too (was in replies.py).
LEASE_CITE = re.compile(r"\bLease\s+(?:Section|Article|Paragraph)\s+(\d+(?:\.\d+)*)|\bLease,?\s+page\s+(\d+)", re.I)


def lease_cite(clause):
    """How a clause is cited: "Lease Section 3.1" for a numbered section ("3.1. Monthly Rent"), "Lease Article 7"
    for an article ("ARTICLE 7"), "Lease, page 1" for a clause the profile gives no number."""
    found = SECTION_NUMBER.match(clause.section or "")
    if not found:
        return f"Lease, page {clause.page}"
    return f"Lease {(found.group(1) or 'section').capitalize()} {found.group(2)}"


def lease_lines(profile):
    """The profile for the system prompt's YOUR LEASE: a line per clause, in LABELS' words, with its cite and its
    words; a clause the reading found no provision for, or did not read, said so. No field name."""
    lines = []
    for name in type(profile).model_fields:
        clause = getattr(profile, name)
        if clause is None:
            lines.append(f"- {LABELS[name]}: not read from this lease")
        elif not clause.present:
            lines.append(f"- {LABELS[name]}: the tool's reading found no such clause")
        else:
            lines.append(f"- {LABELS[name]} (cite as {lease_cite(clause)}): \"{' '.join(clause.quote.split())}\"")
    return "\n".join(lines)


def check_quotes(profile, pages):
    """Every quote must appear verbatim starting on the page it claims. May run onto the next page."""
    page_text = {p["page"]: squash(p["text"]) for p in pages}
    for name, clause in profile:
        if clause is None:
            print(f"  ??   {name}: not read")
            continue
        if not clause.present:
            print(f"  --   {name}: not present")
            continue
        ok = quote_found(clause.quote, page_text, clause.page)
        print(f"  {'OK  ' if ok else 'FAIL'} {name}  p{clause.page}  {clause.section}")
        if not ok:
            print(f"        {clause.quote[:120]!r}")


# ---- Lease Clauses: the lease text split at its numbered headings ("5.4. Vehicles."), and the clauses that use
# words from what the tenant wrote. For a story no playbook covers: the tenant sees the parts of their own lease
# on the subject, as printed. No model involved.

HEADING = re.compile(r"(?<![\d.])(\d{1,2})\.(\d{1,2})\.\s+([A-Z][A-Za-z ,'’&/-]{2,50}?)\.")
# A page's running header or footer ("Residential Lease Agreement (Florida) | Page 2 of 12"), at the start or the end of
# its text. Was matched anywhere in the joined text, up to 80 characters before the bar, which took real words with it
# ("the tenancy shall become mont by either Party", Section 2.4; TODO item 82); now taken off each page before the
# pages are joined.
FOOTER = re.compile(r"^\s*[^.|\n]{0,80}\|\s*Page \d+ of \d+\s*|\s*[^.|\n]{0,80}\|\s*Page \d+ of \d+\s*$")
ARTICLE = re.compile(r"\s*ARTICLE \d+\b.*$")                  # the next article's heading, after a clause


def lease_text(pages):
    """The lease's pages joined into one text, each page's running header or footer taken off (FOOTER), and where
    each page starts in it, as [(offset, page number)]."""
    text, starts = "", []
    for p in pages:
        starts.append((len(text), p["page"]))
        text += FOOTER.sub(" ", p["text"]) + "\n"
    return text, starts


def lease_clauses(pages):
    """The lease's numbered clauses, in order: [{"number": "5.4", "title": "Vehicles", "page": 2, "text": ...,
    "start": ..., "end": ...}], start and end being where the clause sits in lease_text.
    A heading counts only if its number follows the last one closely (the same section a little further on,
    or the next section or two from its start), so a cross-reference inside a clause ("Section 22.1. Landlord
    may refuse cash" in 3.2) is not taken for a new clause."""
    text, starts = lease_text(pages)
    heads, last = [], (0, 0)
    for m in HEADING.finditer(text):
        number = (int(m.group(1)), int(m.group(2)))
        same_section = number[0] == last[0] and 0 < number[1] - last[1] <= 3
        next_section = 0 < number[0] - last[0] <= 2 and number[1] <= 2
        if same_section or next_section:
            heads.append((m, number))
            last = number
    clauses = []
    for i, (m, number) in enumerate(heads):
        end = heads[i + 1][0].start() if i + 1 < len(heads) else len(text)
        page = max(pg for at, pg in starts if at <= m.start())
        body = ARTICLE.sub("", " ".join(text[m.end():end].split())).strip()
        clauses.append({"number": f"{number[0]}.{number[1]}", "title": " ".join(m.group(3).split()),
                        "page": page, "text": body, "start": m.start(), "end": end})
    return clauses


# ---- Search the lease (TODO item 82): the profile holds sixteen clauses, not the whole lease, and from them the model
# said "the lease does not contain a holdover clause" and "the lease does not mention any late fee" though the test
# lease has both (2.4, 3.3). The model searches the whole text first; a phrase found nowhere in it is a known absence.

def plain(text):
    """The text's letters and digits only, lowercase, with where each sits in the text: the PDF text breaks words
    ("air -conditioning", "warra nty"), so spaces, hyphens, and punctuation are left out of a search."""
    kept = [(ch.lower(), i) for i, ch in enumerate(text) if ch.isalnum()]
    return "".join(ch for ch, _ in kept), [i for _, i in kept]


def find_in_lease(phrase, pages, limit=5):
    """Where a phrase is in the lease's text: the numbered clauses that hold it, in order, at most `limit`
    (lease_clauses' dicts), and the pages that hold it outside any numbered clause, as [(page, a passage around
    it)]. Spaces, hyphens, punctuation, and capitals are ignored (plain); a phrase of three letters or digits or
    fewer ("AC") must stand as a whole word."""
    text, starts = lease_text(pages)
    wanted, _ = plain(phrase)
    if not wanted:
        return [], []
    if len(wanted) <= 3:
        hits = [m.start() for m in re.finditer(r"(?<![A-Za-z0-9])" + re.escape(phrase.strip()) + r"(?![A-Za-z0-9])", text, re.I)]
    else:
        flat, where = plain(text)
        hits = [where[m.start()] for m in re.finditer(re.escape(wanted), flat)]
    every, clauses, outside = lease_clauses(pages), [], []
    for c in every:
        if any(c["start"] <= h < c["end"] for h in hits) and len(clauses) < limit:
            clauses.append(c)
    covered = [(c["start"], c["end"]) for c in every]
    for h in hits:
        if not any(a <= h < b for a, b in covered):
            page = max(pg for at, pg in starts if at <= h)
            if page not in [pg for pg, _ in outside]:
                outside.append((page, " ".join(text[max(0, h - 200):h + 300].split())))
    return clauses, outside
