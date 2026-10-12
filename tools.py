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
from citations import cites_in, is_in
import config
from config import shorten, squash
from corpus import playbooks, statute
from deterministic import matter_deadlines
from lease import LEASE_CITE, find_in_lease
from record import active_playbooks, append_event, element_status, matter_dir, read_events, save
from sheet import parse_answer, shown
from skills import skills
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


# ---- Load Skill: the model picks the skills that fit the tenant's situation. A loaded skill's instructions and statute
# sections are in the system prompt from the next model call (prompt.system_prompt), for the rest of the matter.

@tool
def load_skill(name: str) -> str:
    """Load one of this tool's skills. A skill is a set of instructions for one kind of situation (a deposit not
    returned, a repair not made, a notice received), with the statute sections it rests on. SKILLS in your instructions
    lists every skill with what it covers. Before you answer about the tenant's situation, load each skill that fits
    it; more than one may fit, and do not load one that does not. Once loaded, the skill's instructions appear in
    LOADED SKILLS and its sections in THE STATUTE, in your instructions for the rest of the matter, so load it once.
    name: the skill's name exactly as SKILLS gives it."""
    if name not in skills:
        return f"No skill named {name!r}. The skills there are: {', '.join(skills)}."
    if name in record.matter["skills"]:
        return f"The skill {name} is already loaded. Its instructions are in LOADED SKILLS."
    record.add_skill(name)
    return f"Loaded {name}. Its instructions are now in LOADED SKILLS and its statute sections in THE STATUTE."


# ---- Lease Search (TODO item 82): YOUR LEASE holds the clauses the tool reads, not the whole lease, and from them the
# model said the test lease had no holdover clause and no late fee (it has both, 2.4 and 3.3). The model searches the
# whole lease text before it says the lease does or does not say something.

SEARCH_SHOWN = 1500                                      # characters of one clause the model gets


@tool
def search_lease(phrase: str) -> str:
    """Find where the tenant's lease says something: every numbered clause in the whole lease text that holds the
    word or phrase (spacing, hyphens, and capitals ignored), with the cite to use and its words. YOUR LEASE holds
    only the clauses the tool reads; call this before you say the lease does or does not say something, and try a
    second wording ("holdover", then "month-to-month") before you say it has no such term. Cite a clause it finds as
    given, (Lease Section 2.4); the program prints its words under your reply."""
    pages = record.lease_pages()
    if not pages:
        return "No lease text is stored for this matter."
    clauses, outside = find_in_lease(phrase, pages)
    append_event("fetch", lease_search=phrase, found=[c["number"] for c in clauses] + [f"page {pg}" for pg, _ in outside])
    if not clauses and not outside:
        return (f"No clause or page of the lease's text ({len(pages)} pages) holds \"{phrase}\". The lease may say it in "
                "other words: try another wording before you say the lease has no such term. If no wording is found, "
                "the tool found nothing on it in the lease's text.")
    lines = [f"\"{phrase}\" is in the lease's text ({len(pages)} pages searched):"]
    for c in clauses:
        words = shorten(c["text"], SEARCH_SHOWN)
        lines.append(f"- Lease Section {c['number']}, {c['title']}, page {c['page']}: \"{words}\"")
    lines += [f"- Lease, page {pg}, outside any numbered clause: \"...{words}...\"" for pg, words in outside]
    lines.append("Cite a clause as given here; the program prints its words under your reply.")
    return "\n".join(lines)


# ---- Propose Facts: the model can suggest a fact, never confirm one. It reads the status in its prompt.
# Confirming is the tenant's, on the intake sheet the chat loop shows after the turn (sheet.run_sheet).

@tool
def propose_facts(facts_json: str) -> str:
    """Suggest facts the tenant stated or implied in this chat. You cannot confirm or record a fact: the tenant
    confirms each suggestion on a sheet the program shows right after your reply. Do not ask them to confirm
    it in the chat. Input: JSON object keyed by element id, each {"value": ..., "how": "stated" or "inferred",
    "said": "the tenant's exact words the value rests on", shortened only with "..." between exact pieces}.
    Dates as YYYY-MM-DD, yes/no as true/false, money as a number, a choice as one of its answers, copied exactly.
    Returns which suggestions were taken and why any were refused."""
    try:
        proposals = json.loads(facts_json)
    except json.JSONDecodeError:
        return "facts_json is not valid JSON."
    kinds = {e.id: e for pb in active_playbooks() for e in pb.spec.elements if "user" in e.source}
    said_by_tenant = " ".join(record.tenant_words())
    taken, refused = [], []
    for fact_id, p in proposals.items():
        if fact_id not in kinds:
            refused.append(f"{fact_id}: not a fact this matter's issues ask for")
            continue
        if p.get("value") is None:
            refused.append(f"{fact_id}: no value given")
            continue
        value, expected = parse_answer(kinds[fact_id].type, shown(p["value"]), kinds[fact_id].choices)
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

# get_deadlines ended the model's turn (return_direct) from TODO item 19 to item 51, so the model could not repeat
# or reword the printed dates. Since item 44 the model gets no dates, and since item 46 the prompt's deadline status tells it
# which deadlines have passed, so now the program prints the listing and the model answers the rest of the
# question after it ("If I get rid of the dog by Friday, am I safe?" got the listing and no answer, eval of
# 2026-10-02). get_cases stopped ending the turn at item 47.

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


def deadline_receipt(listing):
    """What the model gets back from get_deadlines: what was printed, with no date in it (TODO item 44: given
    the dates, the model retyped them when asked again instead of calling the tool)."""
    if listing.startswith("Not yet"):
        return ("The program printed for the tenant that no issue has all its facts confirmed yet. Your instructions "
                "show the open facts.")
    data = json.loads(listing)
    dated = [d for d in data["deadlines"] if "deadline" in d]
    issues = sorted({i for d in data["deadlines"] for i in d["issues"]})
    waiting = sorted(data.get("waiting", {}))
    return (f"The program printed the tenant's deadlines: {len(dated)} dated, for {issues or 'no issue'}"
            + (f"; still waiting for facts: {waiting}" if waiting else "")
            + ". You are not shown the dates; your instructions say which have passed. If the tenant asked only "
            "for the deadlines, add nothing; otherwise answer the rest of the question without writing a date. To "
            "show the deadlines again, call get_deadlines again.")


@tool(response_format="content_and_artifact")
def get_deadlines() -> tuple[str, str]:
    """Compute every deadline from the CONFIRMED facts; the program prints them to the tenant, every field
    included, above your reply. This is the ONLY way to get a date: never count or calculate days yourself.
    You get back only a receipt, with no dates: never write a deadline yourself. Whether one has passed is in
    WHICH DEADLINES HAVE PASSED. To show the deadlines again, call get_deadlines again."""
    listing = deadline_listing()
    return deadline_receipt(listing), listing


# ---- Cases: what courts said, from the case wiki's verified pages. The program prints them for the tenant (a
# "cases" block, agent.turn_blocks), and the model gets the same text to set beside the tenant's facts (rule 8);
# it quotes the cases from it and never retells one in its own words.

def offered_topics():
    """The case topics for the loaded skills' statute sections (wiki.case_topics)."""
    return wiki.case_topics(sorted({s for skill in record.active_skills() for s in skill.sections}))


def topic_named(topic, topics):
    """The case topic the model meant, or None: the name as given, or the same name once quote marks,
    curly apostrophes, letter case, and a trailing case count are set aside (the model once copied
    "Landlord's maintenance duties under 83.51 (9)" from the prompt's list, eval of 2026-10-01)."""
    if topic in topics:
        return topic
    plain = topic.strip().strip('"“”').replace("’", "'").lower()
    keys = {plain, re.sub(r"\s+\(\d+\)$", "", plain)}
    return next((t for t in topics if t.replace("’", "'").lower() in keys), None)


@tool(response_format="content_and_artifact")
def get_cases(topic: str) -> tuple[str, str]:
    """What courts have said on one topic listed in COURT CASES THIS TOOL HAS: every case the tool holds on it, oldest first,
    in the courts' own quoted words with pin pages (the statute version each read, its facts, its rule and
    reasoning, how other cases treat it). The program prints them for the tenant above your reply, and you get
    the same text to apply (rule 8). Call it when the tenant asks what courts said, or when a topic is on the
    point you are applying. Pass the topic exactly as it is listed there. Quote a case only from this result,
    word for word, with its name and page."""
    topics = offered_topics()
    topic = topic_named(topic, topics) or topic
    if topic not in topics:                                # the tenant sees the topics and can ask for one
        listed = "; ".join(sorted(topics)) or "none for these issues"
        return (f"No case topic named {topic!r} for this matter. The program printed this tool's case topics for the tenant.",
                f"This tool has no case topic named \"{topic}\". Its case topics for your issues: {listed}.")
    shown_before = record.session and any(ev["kind"] == "cases_shown" and ev.get("topic") == topic
                                          and ev.get("session") == record.session for ev in read_events())
    if shown_before:                                       # printed once per session: the tenant can scroll up
        return (f"[The cases on {topic!r} were already printed above in this chat, and their words are in your "
                f"earlier get_cases result. Nothing new was printed.]",
                f"The cases on \"{topic}\" are printed above in this chat.")
    pages = wiki.read_pages(wiki.ROOT)
    cases = sorted((p for p in pages.values() if wiki.eligible(p) and wiki.issues_on(p, topic)),
                   key=lambda p: str(p["meta"]["decided"]))
    append_event("cases_shown", topic=topic, cases=[str(p["meta"]["cite"]) for p in cases],
                 **({"unverified": True} if config.WIKI_UNVERIFIED else {}))
    printed = wiki.render_cases(topic)
    return ("The program printed these cases for the tenant, above your reply. Apply them as rule 8 says:\n\n"
            + printed), printed


# ---- Draft Letter: a template filled from the record (TODO 95, 2026-10-11). The program writes what a landlord could
# hold the tenant to: today's date, the lease's names and addresses, the reply-by date, the quotes (each checked
# against the lease profile or the statute), the delivery line, and the signer (a tenant the lease names). The model
# writes only the tenant's account and request, whole sentences printed as written and never put inside a sentence of
# the program's: "I request that you {ask}" printed "I request that you i, Morgan Davis, ... am", and "This letter is
# sent by {delivery_method}" printed "sent by by hand" (student simulation of 2026-10-06). Was also: every confirmed
# date of every active issue under its id ("Tenancy terminated", "Claim notice dated" beside "Claim notice date").
# Dates and dollar amounts now sit in the tenant's sentences, and one the record does not hold is named under the letter.

def pretty(d):
    """date or '2026-07-31' -> 'July 31, 2026'"""
    if isinstance(d, str):
        d = date.fromisoformat(d)
    return f"{d:%B} {d.day}, {d.year}"


def quote_is_real(text):
    """True if text appears verbatim in the lease profile or in a stored statute section."""
    sources = [c.quote for _, c in record.profile.clauses() if c.present] + list(statute.values())
    return any(squash(text) in squash(s) for s in sources)


def sentence(text):
    """The model's words as written, ending with a period unless they already end a sentence."""
    text = text.strip()
    return text if not text or text.endswith((".", "!", "?", '"', "'", "”")) else text + "."


def build_letter(account, request, respond_within_days, delivery_method, signed_by, quotes):
    """Assemble the letter line by line: the program's lines around the tenant's account and request."""
    profile = record.profile
    today = date.today()
    lines = [pretty(today), "",
             profile.landlord_name_and_address.quote, "",
             "Re: " + profile.premises_address.quote, ""]
    if account.strip():
        lines += [sentence(account), ""]
    lines += [sentence(request), f"Please respond by {pretty(today + timedelta(days=respond_within_days))}.", ""]
    for q in quotes:
        lines += [f'{q["cite"]} states: "{q["text"]}"', ""]
    lines += [f"Delivery: {delivery_method.strip()}", "", signed_by.strip()]
    return "\n".join(lines)


# Dates and dollar amounts as people write them: "September 19", "Sept. 19, 2026", "Oct 2nd", "9/19", "9/19/2026",
# "2026-09-19", "$1,850.00".
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
          "november", "december"]
MONTH_DAY = re.compile(r"\b(" + "|".join(MONTHS) + r"|jan|feb|mar|apr|jun|jul|aug|sept?|oct|nov|dec)\.?\s+(\d{1,2})"
                       r"(?:st|nd|rd|th)?\b(?:,?\s+(20\d\d)\b)?", re.I)
SLASH_DAY = re.compile(r"\b(\d{1,2})/(\d{1,2})(?:/(20\d\d))?\b")
ISO_DAY = re.compile(r"\b(20\d\d)-(\d\d)-(\d\d)\b")
AMOUNT = re.compile(r"\$\s?(\d+(?:,\d{3})*(?:\.\d+)?)")
NUMBER = re.compile(r"\d+(?:,\d{3})*(?:\.\d+)?")


def dates_written(text):
    """Each date in the text, as written and as (month, day, year or None): [("Sept. 19", (9, 19, None))]."""
    found = []
    for m in MONTH_DAY.finditer(text):
        month = next(i + 1 for i, name in enumerate(MONTHS) if name.startswith(m.group(1).lower()[:3]))
        found.append((m.group(0), (month, int(m.group(2)), int(m.group(3)) if m.group(3) else None)))
    for m in SLASH_DAY.finditer(text):
        found.append((m.group(0), (int(m.group(1)), int(m.group(2)), int(m.group(3)) if m.group(3) else None)))
    for m in ISO_DAY.finditer(text):
        found.append((m.group(0), (int(m.group(2)), int(m.group(3)), int(m.group(1)))))
    return [(words, day) for words, day in found if 1 <= day[0] <= 12 and 1 <= day[1] <= 31]


def same_day(a, b):
    """Two (month, day, year) dates are the same day; a year left out matches any year."""
    return a[:2] == b[:2] and (a[2] is None or b[2] is None or a[2] == b[2])


def amount(words):
    """'1,850.00' -> 1850.0"""
    return float(words.replace(",", ""))


def not_in_record(text, respond_by):
    """The dates and dollar amounts in the tenant's part of a letter that the record does not hold, as written. A
    date counts when it is today, the reply-by date, or in the tenant's own words (the description, updates, this
    session's messages, recorded messages, confirmed facts, a confirmed date among them) or the lease's quotes; an
    amount when it is a confirmed amount, a number in the tenant's own words, or an amount in the lease's quotes."""
    facts = record.matter["facts"]
    events = read_events()
    tenant = " ".join([record.matter.get("description", ""), *record.tenant_words(),
                       *[ev["text"] for ev in events if ev["kind"] == "tenant_update"],
                       *[f'{ev["sent_on"]} {ev["text"]}' for ev in events if ev["kind"] == "communication"],
                       *[v for v in facts.values() if isinstance(v, str)]])
    lease = " ".join(c.quote for _, c in record.profile.clauses() if c.present and c.quote)
    days = [(d.month, d.day, d.year) for d in (date.today(), respond_by)]
    days += [day for _, day in dates_written(tenant + " " + lease)]
    sums = [float(v) for v in facts.values() if isinstance(v, (int, float)) and not isinstance(v, bool)]
    sums += [amount(n) for n in NUMBER.findall(tenant)] + [amount(n) for n in AMOUNT.findall(lease)]
    missing = [words for words, day in dates_written(text) if not any(same_day(day, d) for d in days)]
    missing += [m.group(0) for m in AMOUNT.finditer(text) if amount(m.group(1)) not in sums]
    return list(dict.fromkeys(missing))


def check_line(missing):
    """The line under a letter naming what the record does not hold, or "" when it holds everything."""
    if not missing:
        return ""
    named = missing[0] if len(missing) == 1 else ", ".join(missing[:-1]) + " and " + missing[-1]
    return (f"[CHECK BEFORE YOU SEND, not part of the letter: the tool did not find {named} in your answers, your "
            f"messages, or your lease. Make sure {'it is' if len(missing) == 1 else 'each is'} right.]")


@tool
def draft_letter(issue: str, posture: str, account: str, request: str, respond_within_days: int,
                 delivery_method: str, signed_by: str, obligation_quote: str = "", obligation_cite: str = "",
                 consequence_quote: str = "", consequence_cite: str = "") -> str:
    """Draft a letter from the tenant to the landlord. The tenant sends it; you never do. The program prints today's
    date, the landlord and the unit as the lease gives them, the reply-by date, the quoted sentences, the delivery
    line, and the signer. You write only the account and the request, in the tenant's voice, and they are printed as
    you write them.
    issue: which of the matter's loaded skills this letter is about, e.g. "deposit_not_returned".
    posture: "preserve" (no quotes), "assert" (adds obligation_quote), "escalate" (adds consequence_quote too).
    account: what happened, in whole sentences in the tenant's first person, from what the tenant has told you: the
      problem and when it started, what the tenant did and when, what the landlord did. Every date and amount as the
      tenant gave it or as confirmed, never one you worked out. No cite and no legal conclusion. "" when the request
      says it all.
    request: what the tenant asks for or states, in whole sentences in the tenant's voice, e.g. "Please return my
      $1,850.00 deposit to 12 Elm St, Gainesville FL 32601." or "I will move out on October 11, 2026."
    respond_within_days: how many days the tenant gives for a reply; the program prints the date.
    delivery_method: how the TENANT will send this letter, printed after "Delivery: ", e.g. "certified mail, return
      receipt requested" or "by hand to the leasing office".
    signed_by: the tenant's name as the lease gives it, without a label such as ("Resident"); several tenants signing
      together, their names separated by commas.
    obligation_quote: the exact lease or statute sentence the request rests on, copied word for word.
    obligation_cite: a reader-facing cite such as "Lease Section 4.3" or "Fla. Stat. 83.49(3)(a)". Never a profile field name.
    consequence_quote / consequence_cite: escalate only; the exact sentence stating what happens if the landlord does not act.
    Rejected: a quote not found in the lease profile or the stored statute; a cite in the account or the request (the
    lease's and the statute's words go in only as obligation_quote or consequence_quote); a signer the lease does not
    name. A date or a dollar amount in the account or the request that is not in the tenant's answers, messages, or
    lease is printed with a line asking the tenant to check it."""
    if issue not in playbooks or issue not in record.matter["skills"]:
        return f"issue must be one of this matter's loaded skills: {record.matter['skills']}"
    if posture not in ("preserve", "assert", "escalate"):
        return "posture must be preserve, assert, or escalate"
    tenant_part = f"{account}\n{request}\n{delivery_method}"
    cited = cites_in(AMOUNT.sub("", tenant_part)) + [m.group(0) for m in LEASE_CITE.finditer(tenant_part)]
    if cited:
        return (f"Rejected: the account or the request cites {', '.join(cited)}. Write them without cites; the lease's "
                "and the statute's words go in only as obligation_quote or consequence_quote, with their cites.")
    names = record.profile.tenant_names.quote or ""        # each signer's words must be among the lease's names
    named = set(re.findall(r"[a-z]+", names.lower()))
    signers = [s for s in re.split(r",|\band\b", signed_by, flags=re.I) if s.strip()]
    labeled = re.search(r'[()"“”]', signed_by)
    if not signers or labeled or (names and any(not set(re.findall(r"[a-z]+", s.lower())) <= named for s in signers)):
        return f'Rejected: signed_by must be a tenant the lease names ("{names}"), without a label.'
    quotes = []
    if posture in ("assert", "escalate"):
        if not quote_is_real(obligation_quote):
            return "Rejected: obligation_quote is not found in the lease profile or the stored statute."
        quotes.append({"cite": obligation_cite, "text": obligation_quote})
    if posture == "escalate":
        if not quote_is_real(consequence_quote):
            return "Rejected: consequence_quote is not found in the lease profile or the stored statute."
        quotes.append({"cite": consequence_cite, "text": consequence_quote})

    letter = build_letter(account, request, respond_within_days, delivery_method, signed_by, quotes)
    check = check_line(not_in_record(tenant_part, date.today() + timedelta(days=respond_within_days)))
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
    return letter + (f"\n\n{check}" if check else "") + "\n\n[NOTE TO TENANT, not part of the letter: " + note + "]"


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

tools = [get_statute_section, search_statute, load_skill, search_lease, propose_facts, get_deadlines, get_cases, draft_letter,
         add_artifact, add_communication]
