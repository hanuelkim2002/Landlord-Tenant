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
from deterministic import matter_deadlines
from record import active_playbooks, append_event, element_status, matter_dir, save
from sheet import parse_answer, shown


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


# ---- Propose Facts: the model can suggest a fact, never confirm one. It reads the status in its prompt.
# Confirming is the tenant's, on the intake sheet the chat loop shows after the turn (sheet.run_sheet).

@tool
def propose_facts(facts_json: str) -> str:
    """Suggest facts the tenant stated or implied in this chat. You cannot confirm or record a fact: the tenant
    confirms each suggestion on a sheet the program shows right after your reply. Do not ask them to confirm
    it in the chat. Input: JSON object keyed by element id, each {"value": ..., "how": "stated" or "inferred",
    "said": "the tenant's exact words the value rests on"}. Dates as YYYY-MM-DD, yes/no as true/false, money
    as a number. Returns which suggestions were taken and why any were refused."""
    try:
        proposals = json.loads(facts_json)
    except json.JSONDecodeError:
        return "facts_json is not valid JSON."
    kinds = {e.id: e.type for pb in active_playbooks() for e in pb.spec.elements if "user" in e.source}
    said_by_tenant = squash(" ".join(record.tenant_words()))
    taken, refused = [], []
    for fact_id, p in proposals.items():
        if fact_id not in kinds:
            refused.append(f"{fact_id}: not a fact this matter's issues ask for")
            continue
        if p.get("value") is None:
            refused.append(f"{fact_id}: no value given")
            continue
        value, expected = parse_answer(kinds[fact_id], shown(p["value"]))
        if expected:
            refused.append(f"{fact_id}: value must be {expected}")
        elif p.get("how") not in ("stated", "inferred"):
            refused.append(f"{fact_id}: how must be stated or inferred")
        elif not p.get("said") or squash(p["said"]) not in said_by_tenant:
            refused.append(f"{fact_id}: said must be the tenant's exact words from this chat")
        elif fact_id in record.matter["facts"] and record.matter["facts"][fact_id] == value:
            refused.append(f"{fact_id}: already confirmed with that value")
        else:
            record.matter["proposed"][fact_id] = {"value": value, "how": p["how"], "basis": p["said"]}
            taken.append(fact_id)
    record.prune_proposals()
    save(record.matter)
    lines = []
    if taken:
        lines.append("Suggested: " + ", ".join(taken) + ". The tenant confirms them on the sheet shown after your reply.")
    if refused:
        lines.append("Refused: " + "; ".join(refused))
    return "\n".join(lines) or "Nothing to suggest."


# ---- Deadlines

@tool
def get_deadlines() -> str:
    """Compute every deadline from the CONFIRMED facts. This is the ONLY way to get a date. Never count or
    calculate days yourself. Works issue by issue: returns the deadlines of every issue whose facts are all
    confirmed or n/a, and under "waiting" the issues whose facts are still open, with those facts. A deadline
    two issues share appears once. The program shows the result to the tenant itself, every field included;
    do not repeat or reword it."""
    waiting = {}
    for issue, rows in element_status().items():
        open_ids = sorted({r["id"] for r in rows if r["status"] in ("proposed", "changed", "missing")})
        if open_ids:
            waiting[issue] = open_ids
    ready = [pb for pb in active_playbooks() if pb.issue not in waiting]
    if not ready:
        return "Not yet. No issue has all its facts confirmed. Still open, by issue: " + json.dumps(waiting)
    deadlines = matter_deadlines(ready, record.matter["facts"], date.today())   # shared ones once
    for pb in ready:
        append_event("deadlines_computed", issue=pb.issue,
                     clocks=[d["clock"] for d in deadlines if pb.issue in d["issues"] and "deadline" in d])
    result = {"deadlines": deadlines}
    if waiting:
        result["waiting"] = waiting            # these issues' dates come once their facts are confirmed
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
    ask = ask.strip().rstrip(".")                          # the sentence below adds its own period
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

tools = [get_statute_section, search_statute, propose_facts, get_deadlines, draft_letter, add_artifact, add_communication]
