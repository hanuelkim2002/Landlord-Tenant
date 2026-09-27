"""Tools: each is a plain function with the @tool decorator. The model never does what these do itself.

With LangChain's @tool, each tool's schema is generated from the function itself: the parameter names and
type hints become the fields, and the docstring becomes the description the model reads. That is why every
docstring here is written to the model, not to a reader of the code. Run `python schemas.py` to see what the
model sees.
"""
import hashlib
import json
from datetime import date, timedelta
from pathlib import Path

from langchain.tools import tool

import record
from config import squash
from corpus import playbooks, statute
from deterministic import compute_deadlines
from record import active_playbooks, append_event, element_status, matter_dir, save


# ---- Statute Lookup

@tool
def get_statute_section(section: str) -> str:
    """Full text of one section of Fla. Stat. ch. 83 pt. II, e.g. "83.505".
    Use when the preloaded sections do not answer the question."""
    append_event("fetch", section=section)
    return statute.get(section, f"No section {section} stored. Available: {sorted(statute)}")


@tool
def search_statute(phrase: str) -> str:
    """Find which sections of ch. 83 pt. II contain a word or phrase. Returns section numbers with a short snippet."""
    hits = []
    for sec, text in statute.items():
        i = text.lower().find(phrase.lower())
        if i >= 0:
            hits.append(f"{sec}: ...{text[max(0, i-80):i+120]}...")
    append_event("fetch", search=phrase)
    return "\n".join(hits) or "No matches."


# ---- Record Facts

@tool
def record_facts(facts_json: str) -> str:
    """Save facts the tenant has CONFIRMED, after you showed them the value and asked. Input: JSON object
    keyed by element id, e.g. {"early_or_periodic": true}. Dates as YYYY-MM-DD. Returns updated element status."""
    confirmed = json.loads(facts_json)
    for fact_id, value in confirmed.items():
        was = record.matter["proposed"].pop(fact_id, {"value": None, "how": "asked", "basis": None})
        record.matter["facts"][fact_id] = value
        append_event("fact_confirmed", id=fact_id, value=value, how=was["how"], basis=was["basis"], proposed_value=was["value"])
    save(record.matter)
    return json.dumps(element_status(), indent=2)


# ---- Deadlines

@tool
def get_deadlines() -> str:
    """Compute every deadline from the CONFIRMED facts, for every issue in this matter. This is the ONLY way
    to get a date. Never count or calculate days yourself. Refuses until every element is confirmed or n/a."""
    waiting = [r["id"] for rows in element_status().values() for r in rows if r["status"] in ("proposed", "changed", "missing")]
    if waiting:
        return "Not yet. These facts are still unconfirmed: " + ", ".join(sorted(set(waiting)))
    result = []
    for pb in active_playbooks():
        rows = compute_deadlines(pb, record.matter["facts"], date.today())
        for d in rows:
            d["issue"] = pb.issue
        result += rows
        append_event("deadlines_computed", issue=pb.issue, clocks=[d["clock"] for d in rows if "deadline" in d])
    return json.dumps(result, indent=2, default=str)


# ---- Draft Letter: a template filled from the record. No model call, so there is nothing to validate:
# every date is today or a confirmed fact, and every quote was checked against the lease profile or the statute.

def pretty(d):
    """date or '2026-07-31' -> 'July 31, 2026'"""
    if isinstance(d, str):
        d = date.fromisoformat(d)
    return d.strftime("%B %d, %Y")


def quote_is_real(text):
    """True if text appears verbatim in the lease profile or in a stored statute section."""
    sources = [c.quote for _, c in record.profile if c.present] + list(statute.values())
    return any(squash(text) in squash(s) for s in sources)


def build_letter(ask, respond_within_days, delivery_method, quotes):
    """Assemble the letter line by line. Every date is today or a confirmed fact; every quote was checked."""
    profile, facts = record.profile, record.matter["facts"]
    today = date.today()
    lines = [pretty(today), "",
             profile.landlord_name_and_address.quote, "",
             "Re: " + profile.premises_address.quote, ""]
    dates_shown = set()
    for pb in active_playbooks():                          # the confirmed dates, labeled by the playbooks' own ids
        for e in pb.spec.elements:
            if e.type == "date" and e.id in facts and e.id not in dates_shown:
                dates_shown.add(e.id)
                lines.append(f"{e.id.replace('_', ' ').capitalize()}: {pretty(facts[e.id])}")
    lines += ["", f"I request that you {ask[0].lower() + ask[1:]}.",
              f"Please respond by {pretty(today + timedelta(days=respond_within_days))}.", ""]
    for q in quotes:
        lines += [f'{q["cite"]} states: "{q["text"]}"', ""]
    lines += [f"This letter is sent by {delivery_method}.", "", profile.tenant_names.quote]
    return "\n".join(lines)


@tool
def draft_letter(issue: str, posture: str, ask: str, respond_within_days: int, delivery_method: str,
                 obligation_quote: str = "", obligation_cite: str = "",
                 consequence_quote: str = "", consequence_cite: str = "") -> str:
    """Draft a letter from the tenant to the landlord. The tenant sends it; you never do.
    issue: which of the matter's issues this letter is about, e.g. "deposit_not_returned".
    posture: "preserve" (no quotes), "assert" (adds obligation_quote), "escalate" (adds consequence_quote too).
    ask: the concrete thing the tenant wants, e.g. "return the $1,850.00 deposit to 12 Elm St, Gainesville FL 32601".
    respond_within_days: how many days the tenant gives for a reply.
    delivery_method: how the TENANT will send this letter, e.g. "certified mail, return receipt requested".
    obligation_quote: the exact lease or statute sentence the ask rests on, copied word for word.
    obligation_cite: a reader-facing cite such as "Lease Section 4.3" or "Fla. Stat. 83.49(3)(a)". Never a profile field name.
    consequence_quote / consequence_cite: escalate only; the exact sentence stating what happens if the landlord does not act.
    Quotes not found in the lease profile or the stored statute are rejected."""
    if issue not in playbooks or issue not in record.matter["issues"]:
        return f"issue must be one of this matter's issues: {record.matter['issues']}"
    if posture not in ("preserve", "assert", "escalate"):
        return "posture must be preserve, assert, or escalate"
    quotes = []
    if posture in ("assert", "escalate"):
        if not quote_is_real(obligation_quote):
            return "Rejected: obligation_quote is not found in the lease profile or the stored statute."
        quotes.append({"cite": obligation_cite, "text": obligation_quote})
    if posture == "escalate":
        if not quote_is_real(consequence_quote):
            return "Rejected: consequence_quote is not found in the lease profile or the stored statute."
        quotes.append({"cite": consequence_cite, "text": consequence_quote})

    letter = build_letter(ask, respond_within_days, delivery_method, quotes)
    filename = f"draft_{date.today()}_{issue}_{posture}.txt"
    (matter_dir() / filename).write_text(letter)
    append_event("draft", issue=issue, posture=posture, cites=[q["cite"] for q in quotes], file=filename)
    note = playbooks[issue].guidance["postures"]["notice_sufficiency"]
    return letter + "\n\n[NOTE TO TENANT, not part of the letter: " + note + "]"


# ---- Add Artifact

@tool
def add_artifact(path: str, note: str) -> str:
    """Store a file the tenant provides (photo, email export, receipt) in the matter record.
    path: where the file is on this computer. note: what it is, in the tenant's words."""
    src = Path(path)
    data = src.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    dest = matter_dir() / "artifacts" / f"{sha[:12]}_{src.name}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    append_event("artifact", file=src.name, sha256=sha, note=note)
    return f"Stored {src.name} as {dest.name}"


# ---- Add Communication

@tool
def add_communication(sent_on: str, sender: str, recipient: str, channel: str, text: str) -> str:
    """Record one message between tenant and landlord in the matter record.
    sent_on: the date on the message, YYYY-MM-DD. sender / recipient: who wrote it and who received it.
    channel: email, text message, letter, or in person. text: the message copied verbatim, never summarized."""
    try:
        date.fromisoformat(sent_on)
    except ValueError:
        return "sent_on must be a date like 2026-08-03"
    append_event("communication", sent_on=sent_on, sender=sender, recipient=recipient, channel=channel, text=text)
    return f"Recorded {channel} from {sender} to {recipient} dated {sent_on}."


# ---- Tools List: what the agent may call. A new tool goes here after it is defined above.

tools = [get_statute_section, search_statute, record_facts, get_deadlines, draft_letter, add_artifact, add_communication]
