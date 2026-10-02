"""Lease Intake: read the PDF, extract the profile with Gemma, check every quote against the page."""
import hashlib
import json
import math
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


# ---- Lease Clauses: the lease text split at its numbered headings ("5.4. Vehicles."), and the clauses that use
# words from what the tenant wrote. For a story no playbook covers: the tenant sees the parts of their own lease
# on the subject, as printed. No model involved.

HEADING = re.compile(r"(?<![\d.])(\d{1,2})\.(\d{1,2})\.\s+([A-Z][A-Za-z ,'’&/-]{2,50}?)\.")
FOOTER = re.compile(r"[^.|]{0,80}\|\s*Page \d+ of \d+\s*")    # a page's running footer, where a clause runs over pages
ARTICLE = re.compile(r"\s*ARTICLE \d+\b.*$")                  # the next article's heading, after a clause


def lease_clauses(pages):
    """The lease's numbered clauses, in order: [{"number": "5.4", "title": "Vehicles", "page": 2, "text": ...}].
    A heading counts only if its number follows the last one closely (the same section a little further on,
    or the next section or two from its start), so a cross-reference inside a clause ("Section 22.1. Landlord
    may refuse cash" in 3.2) is not taken for a new clause."""
    text, starts = "", []                              # the pages joined, and where each page begins
    for p in pages:
        starts.append((len(text), p["page"]))
        text += p["text"] + "\n"
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
        body = ARTICLE.sub("", FOOTER.sub(" ", " ".join(text[m.end():end].split()))).strip()
        clauses.append({"number": f"{number[0]}.{number[1]}", "title": " ".join(m.group(3).split()),
                        "page": page, "text": body})
    return clauses


# Everyday words a tenant uses, and the words a lease uses for the same thing. Small and explicit: extend it when
# a story's clause is missed. Keys and values are matched as stems (stem, below).
LEASE_WORDS = {
    "roommate": ["joint", "several", "occupant"],
    "cotenant": ["joint", "several", "occupant"],
    "split": ["joint", "several"],
    "car": ["vehicle", "park"],
    "truck": ["vehicle", "park"],
    "tow": ["vehicle", "park"],
    "noise": ["disturb", "nuisance", "neighbor"],
    "loud": ["disturb", "nuisance", "neighbor"],
    "party": ["disturb", "nuisance", "neighbor"],
    "dog": ["pet", "animal"],
    "cat": ["pet", "animal"],
    "smoke": ["smoking"],
    "sublet": ["sublease", "assign"],
    "guest": ["guest", "occupant"],
    "key": ["lock", "key"],
}
STOP = set("""the and for that this with have has had was were are but not you your yours they them their there
him his her she our out all any can could would should will just about from into than then when what which who
whom why how also very more most some such only over back even still because been being does did doing done
said says say tell told make made get got going know want wants need needs like time day days week weeks month
months year years thing things way lot lots really one two three four first last since until while after before
without within anyone anything someone something everyone everything nothing whole half both each every other
another same own able again away here keep keeps kept stop stopped
pay paid paying payment landlord tenant lease rent premises agreement shall""".split())


def stem(word):
    """A rough stem, enough to match "parking" with "park" and "parties" with "party"."""
    w = re.sub(r"[^a-z]", "", word.lower())
    for suffix, keep in (("ies", "y"), ("ing", ""), ("ed", ""), ("s", "")):
        if w.endswith(suffix) and len(w) - len(suffix) >= 3 and not w.endswith("ss"):
            return w[: len(w) - len(suffix)] + keep
    return w


def stems(text):
    return {stem(w) for w in re.findall(r"[A-Za-z’']+", text)}


def matches(term, words):
    """True if a stem is among a clause's stems: exactly for a stem under four letters; otherwise as the start
    of a longer one ("disturb" in "disturbance"), or the other way round when the clause's word is six letters
    or more, so "room" never matches "roommate"."""
    if len(term) < 4:
        return term in words
    return any(w.startswith(term) or (len(w) >= 6 and term.startswith(w)) for w in words)


def clauses_about(text, pages, limit=3):
    """The lease clauses on the subject of the tenant's text, best first, at most `limit`: a clause whose title
    uses one of the tenant's words or a LEASE_WORDS word ("Vehicles" for "towed"), or whose text uses a
    LEASE_WORDS words ("disturbs neighbors" for "parties"). The tenant's own words count only in titles, where a
    lease names its subjects; in the body they would match too much ("half", "cover"). A clause found by its
    text alone needs two LEASE_WORDS words. A word counts for more the fewer clauses use it, and a title match
    counts double."""
    clauses = lease_clauses(pages)
    if not clauses:
        return []
    titles = [stems(c["title"]) for c in clauses]
    bodies = [stems(c["title"] + " " + c["text"]) for c in clauses]
    said = {t for t in stems(text) - stems(" ".join(STOP)) if len(t) >= 3}
    mapped = {stem(x) for t in said for x in LEASE_WORDS.get(t, [])}

    def weight(term):
        used = sum(matches(term, b) for b in bodies)
        return math.log(len(clauses) / used) if used else 0

    scored = []
    for c, title, body in zip(clauses, titles, bodies):
        in_title = [t for t in said | mapped if matches(t, title)]
        in_body = [t for t in mapped if matches(t, body) and t not in in_title]
        if in_title or len(in_body) >= 2:
            scored.append((sum(2 * weight(t) for t in in_title) + sum(weight(t) for t in in_body), c))
    return [c for _, c in sorted(scored, key=lambda x: -x[0])[:limit]]
