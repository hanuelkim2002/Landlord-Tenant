"""Tools: each is a plain function with the @tool decorator. The model never does what these do itself.

With LangChain's @tool, each tool's schema is generated from the function itself: the parameter names and
type hints become the fields, and the docstring becomes the description the model reads. That is why every
docstring here is written to the model, not to a reader of the code. Run `python schemas.py` to see what the
model sees.
"""
import hashlib
import json
import re
from datetime import date, timedelta
from pathlib import Path

from langchain.tools import tool

import record
from citations import is_in
import config
from config import squash
from corpus import playbooks, statute
from deterministic import matter_deadlines
from record import active_playbooks, append_event, element_status, matter_dir, read_events, save
from sheet import parse_answer, shown
import wiki


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
    "said": "the tenant's exact words the value rests on", shortened only with "..." between exact pieces}.
    Dates as YYYY-MM-DD, yes/no as true/false, money as a number. Returns which suggestions were taken and why
    any were refused."""
    try:
        proposals = json.loads(facts_json)
    except json.JSONDecodeError:
        return "facts_json is not valid JSON."
    kinds = {e.id: e.type for pb in active_playbooks() for e in pb.spec.elements if "user" in e.source}
    said_by_tenant = " ".join(record.tenant_words())
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
        elif not p.get("said") or not is_in(p["said"], said_by_tenant):   # each piece around "..." exact
            refused.append(f"{fact_id}: said must be the tenant's exact words from this chat (\"...\" may join "
                           "exact pieces)")
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

# get_deadlines and get_cases end the model's turn (return_direct): when every tool the model called in a step
# is one of them, the agent stops after the tool, the chat loop prints what the program made, and the model
# writes no reply after it, so it cannot repeat or reword a printed line (TODO item 19).

def open_facts_by_issue():
    """The facts each active issue still needs (proposed, changed, or missing), by issue. An issue with none is
    ready: its deadlines can be computed."""
    waiting = {}
    for issue, rows in element_status().items():
        open_ids = sorted({r["id"] for r in rows if r["status"] in ("proposed", "changed", "missing")})
        if open_ids:
            waiting[issue] = open_ids
    return waiting


def deadline_listing():
    """Every deadline the confirmed facts give, as JSON: {"deadlines": [...], "waiting": {issue: [open facts]}},
    issue by issue (an issue is ready when none of its facts is proposed, changed, or missing; a deadline two
    issues share appears once), or "Not yet. ..." with the open facts when no issue is ready. Writes a
    deadlines_computed event per ready issue. What the program prints, through render_deadlines."""
    waiting = open_facts_by_issue()
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


def deadline_status():
    """DEADLINE STATUS, for the system prompt: each deadline of the ready issues, whose it is, what it counts
    from, its cite, and whether it has passed, with no date in it, then the issues still waiting and what for.
    So the model can apply a condition such as "within the 30-day period" from the program's "passed" or
    "upcoming", never from dates of its own (TODO item 46). Logs nothing: the prompt is rebuilt on every call."""
    waiting = open_facts_by_issue()
    ready = [pb for pb in active_playbooks() if pb.issue not in waiting]
    lines = []
    for d in matter_deadlines(ready, record.matter["facts"], date.today()):
        issues = ", ".join(d["issues"])
        if "deadline" not in d:
            lines.append(f"- {d['clock']} [{issues}]: no date ({d['status']})")
            continue
        start = d["from"].split()[0]                       # the trigger's id; its date stays out
        lines.append(f"- {d['clock']} [{issues}]: the {d['actor']}'s, {d['rule']} {start}, Fla. Stat. {d['cite']}: "
                     f"{d['status']}")
    lines += [f"- waiting [{issue}]: no deadline until these are confirmed: {', '.join(ids)}"
              for issue, ids in waiting.items()]
    return "\n".join(lines) or "none: no active issue has a deadline this tool computes"


def deadline_receipt(listing):
    """What the model gets back from get_deadlines: what was printed, with no date in it (TODO item 44: given
    the dates, the model retyped them when asked again instead of calling the tool)."""
    if listing.startswith("Not yet"):
        return ("The program printed for the tenant that no issue has all its facts confirmed yet. ELEMENT STATUS "
                "shows the open facts.")
    data = json.loads(listing)
    dated = [d for d in data["deadlines"] if "deadline" in d]
    issues = sorted({i for d in data["deadlines"] for i in d["issues"]})
    waiting = sorted(data.get("waiting", {}))
    return (f"The program printed the tenant's deadlines: {len(dated)} dated, for {issues or 'no issue'}"
            + (f"; still waiting for facts: {waiting}" if waiting else "")
            + ". You are not shown the dates. To show the deadlines again, call get_deadlines again.")


@tool(response_format="content_and_artifact", return_direct=True)
def get_deadlines() -> tuple[str, str]:
    """Compute every deadline from the CONFIRMED facts. This is the ONLY way to get a date. Never count or
    calculate days yourself. The program prints the deadlines to the tenant, every field included, and your
    turn ends there: call it alone. You get back only a receipt, with no dates: never write a deadline
    yourself, and to show the deadlines again, call get_deadlines again."""
    listing = deadline_listing()
    return deadline_receipt(listing), listing


# ---- Cases: what courts said, from the case wiki's verified pages. The program prints the result to the tenant
# (agent.show_turn), so the model never retells a case.

def offered_topics():
    """The case topics for the active issues' statute sections (wiki.case_topics)."""
    return wiki.case_topics(sorted({s for pb in active_playbooks() for s in pb.sections}))


def topic_named(topic, topics):
    """The CASE TOPICS name the model meant, or None: the name as given, or the same name once quote marks,
    curly apostrophes, letter case, and a trailing case count are set aside (the model once copied
    "Landlord's maintenance duties under 83.51 (9)" from the prompt's list, eval of 2026-10-01)."""
    if topic in topics:
        return topic
    plain = topic.strip().strip('"“”').replace("’", "'").lower()
    keys = {plain, re.sub(r"\s+\(\d+\)$", "", plain)}
    return next((t for t in topics if t.replace("’", "'").lower() in keys), None)


@tool(response_format="content_and_artifact", return_direct=True)
def get_cases(topic: str) -> tuple[str, str]:
    """What courts have said on one topic listed in CASE TOPICS: the program prints every case the tool holds
    on it, oldest first, in the courts' own quoted words, and your turn ends there. Use only when the tenant
    asks what courts or cases say, and call it alone. Pass the topic exactly as CASE TOPICS lists it. You get
    back only the names of the cases printed, not their text: never quote, summarize, rank, or reword a case,
    and never say whether one applies to the tenant."""
    topics = offered_topics()
    topic = topic_named(topic, topics) or topic
    if topic not in topics:                                # the tenant sees the topics and can ask for one
        listed = "; ".join(sorted(topics)) or "none for these issues"
        return (f"No case topic named {topic!r} for this matter. The program printed the CASE TOPICS for the tenant.",
                f"This tool has no case topic named \"{topic}\". Its case topics for your issues: {listed}.")
    shown_before = record.session and any(ev["kind"] == "cases_shown" and ev.get("topic") == topic
                                          and ev.get("session") == record.session for ev in read_events())
    if shown_before:                                       # printed once per session: the tenant can scroll up
        return (f"[The cases on {topic!r} were already printed above in this chat. Nothing new was printed.]",
                f"The cases on \"{topic}\" are printed above in this chat.")
    pages = wiki.read_pages(wiki.ROOT)
    cases = sorted((p for p in pages.values() if wiki.eligible(p) and wiki.issues_on(p, topic)),
                   key=lambda p: str(p["meta"]["decided"]))
    append_event("cases_shown", topic=topic, cases=[str(p["meta"]["cite"]) for p in cases],
                 **({"unverified": True} if config.WIKI_UNVERIFIED else {}))
    printed = "; ".join(f"{p['name']}, {wiki.citation(p['meta'])}" for p in cases)
    return (f"The program printed the cases on {topic!r} for the tenant, oldest first: {printed}. Its last line "
            f"says this tool does not decide whether any of them applies to the tenant."), wiki.render_cases(topic)


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
    # The same letter again in the same session (seen in m-026) is already on the tenant's screen: nothing is
    # written or logged. Same means this session drafted this file and the text has not changed.
    drafted_here = record.session and any(ev["kind"] == "draft" and ev.get("file") == filename
                                          and ev.get("session") == record.session for ev in read_events())
    if drafted_here and (matter_dir() / filename).read_text() == letter:
        return (f"[The same letter was already drafted in this session ({filename}) and appears above. Nothing "
                "new was drafted.]")
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

tools = [get_statute_section, search_statute, propose_facts, get_deadlines, get_cases, draft_letter, add_artifact,
         add_communication]
