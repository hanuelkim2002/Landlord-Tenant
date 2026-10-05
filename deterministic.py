"""Deterministic Layer: element status and date arithmetic (no model), plus the two one-shot intake calls."""
import json
import re
from datetime import date, datetime, timedelta


from calendars import court_calendar, holidays_in
from config import agent_llm, squash
from lease import LABELS, lease_cite


# ---- Element Status

def lease_value(kind, quote):
    """Read a lease quote as the element's type, so it can be compared with the tenant's answer. Dates as
    printed ("September 30, 2027", "9/30/2027", "2027-09-30") and dollar amounts ("$1,850.00"). None when
    the quote cannot be read that way; then nothing is compared."""
    if kind == "date":
        for fmt in ("%B %d, %Y", "%b %d, %Y", "%m/%d/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(quote.strip().rstrip("."), fmt).date().isoformat()
            except ValueError:
                pass
    if kind == "money":
        found = re.search(r"\$([\d,]+(?:\.\d\d)?)", quote)
        if found:
            amount = float(found.group(1).replace(",", ""))
            return int(amount) if amount == int(amount) else amount
    return None


def lease_differs(e, profile, tenant_value):
    """The lease's exact words when the element names a lease field (compare_to) and the lease's value,
    read as the element's type, differs from the tenant's. Otherwise None. The tool shows both; it does
    not decide which is right."""
    if not e.compare_to or profile is None:
        return None
    clause = getattr(profile, e.compare_to.replace("lease_profile.", ""))
    if not clause.present:
        return None
    lease = lease_value(e.type, clause.quote)
    if lease is None or lease == tenant_value:
        return None
    return clause.quote


def check_elements(playbook, profile, facts, proposed):
    """For each element: known (confirmed), changed (confirmed, but a later update suggests a different value),
    proposed (needs the tenant's confirmation), missing, or n/a. A row whose tenant value differs from the
    lease field named in compare_to also carries lease_says, the lease's exact words.
    facts = confirmed answers keyed by element id. proposed = unconfirmed answers with how and basis."""
    rows = []
    for e in playbook.spec.elements:
        # Elements that only matter if another CONFIRMED fact is true. n/a until then.
        if e.applies_if and not facts.get(e.applies_if):
            rows.append({"id": e.id, "status": "n/a"})
            continue

        value, found_in = None, None
        for src in e.source:
            if src == "user" and e.id in facts:
                value, found_in = facts[e.id], "user"
            elif src.startswith("lease_profile."):
                clause = getattr(profile, src.replace("lease_profile.", ""))
                if clause.present:
                    value, found_in = clause.quote, src
            if value is not None:
                break

        # A confirmed fact with a different value waiting in proposed: show both, the tenant decides.
        # Only for facts the tenant confirmed; a value read from the lease is not changed this way.
        if found_in == "user" and e.id in proposed and proposed[e.id]["value"] != value:
            p = proposed[e.id]
            rows.append({"id": e.id, "status": "changed", "value": value, "new_value": p["value"],
                         "how": p["how"], "basis": p["basis"],
                         "ask": f"The tenant confirmed {value}; their update suggests {p['value']}. Ask which is "
                                f"right: " + playbook.guidance["questions"][e.id]})
        elif value is not None:
            rows.append({"id": e.id, "status": "known", "value": value, "from": found_in})
        elif e.id in proposed:
            p = proposed[e.id]
            rows.append({"id": e.id, "status": "proposed", "value": p["value"], "how": p["how"], "basis": p["basis"],
                         "ask": "Confirm with the tenant: " + playbook.guidance["questions"][e.id]})
        else:
            rows.append({"id": e.id, "status": "missing", "ask": playbook.guidance["questions"][e.id]})
            continue

        row = rows[-1]                                     # the tenant's value this row shows, if any
        tenant_value = row.get("new_value", row.get("value")) if row.get("from", "user") == "user" else None
        says = lease_differs(e, profile, tenant_value) if tenant_value is not None else None
        if says:
            row["lease_says"] = says
    return rows


# ---- Deadlines: the only date arithmetic in the project.

def court_days(start, days, direction, county):
    """Count court business days from start: one day at a time, the start day not counted, skipping Saturdays,
    Sundays, and every holiday in the calendar of the circuit that includes the county. Returns (date, the
    counting line to show with it), or (None, why it cannot be computed): no calendar for the county, or a day
    in a year with no memorandum loaded. Never guesses a holiday."""
    cal = court_calendar(county)
    if cal is None:
        return None, f"not computed: no court holiday calendar for {county + ' County' if county else 'the rental county'}"
    holidays = holidays_in(cal)
    step = timedelta(days=1 if direction == "after" else -1)
    day, counted, years = start, 0, set()
    while counted < days:
        day += step
        if str(day.year) not in cal["years"]:
            return None, f"not computed: no {cal['circuit']} holiday memorandum loaded for {day.year}"
        years.add(day.year)
        if day.weekday() < 5 and day not in holidays:      # Monday to Friday, not a court holiday
            counted += 1
    used = ", ".join(f"{y} (issued {cal['years'][str(y)]['issued_on']})" for y in sorted(years))
    return day, (f"court business days, start day not counted, Saturdays, Sundays, and every holiday in the "
                 f"{cal['circuit']} Chief Judge's memorandum skipped ({used}). ASSUMPTION: the counting rule and "
                 f"which holidays count are open questions; show this line with the date.")


def compute_deadlines(playbook, facts, today):
    """Date arithmetic only. Dates in facts are strings like '2026-07-31'."""
    out = []
    for c in playbook.spec.clocks:
        # Same applies_if rule as elements: skip clocks that don't apply.
        if c.applies_if and not facts.get(c.applies_if):
            continue
        # Can't compute without the trigger date. Say which one is needed.
        if c.trigger not in facts:
            out.append({"clock": c.id, "status": "need date for " + c.trigger})
            continue

        # Turn "2026-07-31" into a real date, then add or subtract the day count.
        start = date.fromisoformat(facts[c.trigger])
        counting = playbook.counting["convention"]
        if c.count == "court_business_days":
            deadline, counting = court_days(start, c.days, c.direction, facts.get("premises_county"))
            if deadline is None:                           # no calendar for the county or the year: say so
                out.append({"clock": c.id, "status": counting})
                continue
        elif c.direction == "after":
            deadline = start + timedelta(days=c.days)
        else:
            deadline = start - timedelta(days=c.days)

        # One result per clock, carrying the cite and the counting assumption
        # so whoever reads it can see where the number came from.
        row = {
            "clock": c.id,
            "actor": c.actor,
            "from": f"{c.trigger} {start}",
            "rule": f"{c.days} {'court business days' if c.count == 'court_business_days' else 'days'} {c.direction}",
            "deadline": deadline,
            "status": "passed" if deadline < today else "upcoming",
            "cite": c.cite,
            "counting": counting,
        }
        if c.shown_with and c.shown_with in facts:          # e.g. the date the notice itself states, beside ours
            row["shown_with"] = f"{c.shown_with} {facts[c.shown_with]}"
        out.append(row)
    return out


def matter_deadlines(playbooks, facts, today):
    """compute_deadlines for every playbook of the matter, with a deadline two playbooks share listed once and
    tagged with every issue that has it. Shared means the same clock id, cite, and result (date and status);
    two different rules that happen to share an id stay separate. Each row carries "issues", a list."""
    merged = []
    for pb in playbooks:
        for d in compute_deadlines(pb, facts, today):
            same = next((m for m in merged if m["clock"] == d["clock"] and m.get("cite") == d.get("cite")
                         and m.get("deadline") == d.get("deadline") and m["status"] == d["status"]), None)
            if same:
                same["issues"].append(pb.issue)
            else:
                merged.append({**d, "issues": [pb.issue]})
    return merged


# ---- Options: whether each thing the statute lets the tenant do is open on the confirmed facts, and how far its
# steps have got (TODO item 72). A reply had told the tenant how to end the lease over an AC not repaired, and only
# the next reply said an AC may not be a duty 83.56(1) reaches; so the program decides openness first.
#
# What the tool knows (TODO item 81, the author's decision of 2026-10-04): each condition (gate) is met through one
# of its ways (a confirmed fact, a clock, a lease clause, something the tenant can check, law outside the tool), and
# the program says which of five things it is: known (met, not met, or not met yet), something the tenant can tell
# the tool (a fact the sheet asks), something the tenant can check (a part of the lease the tool has not read, a
# local code, a document), not settled (an open question), or outside the tool. The model said "the lease does not
# mention air conditioning" from a lease it had not read whole, and called ending the lease over an AC not settled
# on the statute alone while the lease promised the repair.

# The state of a way or a gate, best first: a gate takes the best state among its ways, since any way meets it.
STATES = ["met", "tell", "check", "not settled", "outside", "not met yet", "not met"]
# What each state means for the condition, and what the tool knows of it, in words for the prompt.
STATUS = {"met": "met", "not met": "not met", "not met yet": "not met yet", "tell": "not known yet",
          "check": "not known yet", "not settled": "not settled", "outside": "outside the tool"}
KNOWLEDGE = {"met": "known", "not met": "known", "not met yet": "known", "tell": "the tenant can tell the tool",
             "check": "the tenant can check", "not settled": "not settled", "outside": "outside the tool"}


def lease_note(field, profile):
    """Whether the tool read the lease clause a way rests on, in words: read (with the cite to use), read and found
    no such clause, or not read (a profile read before the clause was added, or no profile)."""
    clause = getattr(profile, field, None) if profile is not None else None
    if clause is None:
        return f"the tool has not read the part of the lease on {LABELS[field]}"
    if not clause.present:
        return f"the tool's reading of the lease found no clause on {LABELS[field]}"
    return f"the tool has read the lease's clause on {LABELS[field]}, {lease_cite(clause)}"


def way_state(w, playbook, facts, clock_rows, profile):
    """One way's state (STATES) and why, in plain words: a fact or clock confirmed one way or the other is known (or
    not settled, through its open question); a fact not confirmed is one the tenant can tell the tool on the sheet,
    or can check when it rests on a lease clause the tool has not read; a clock waits for its start date (the tenant
    can tell it) or cannot be counted (outside the tool); a check is the tenant's to check; outside is outside."""
    questions = playbook.guidance["questions"]
    note = lease_note(w.lease, profile) if w.lease else ""
    otherwise = {"closed": "not met", "unsettled": "not settled", "later": "not met yet"}[w.otherwise]
    if w.check:
        return "check", " ".join(w.check.split()) + (f"; {note}" if note else "")
    if w.outside:
        return "outside", " ".join(w.outside.split())
    if w.fact:
        if w.fact in facts:
            return ("met", "") if facts[w.fact] == w.equals else (otherwise, " ".join(w.when_otherwise.split()))
        if w.lease and (profile is None or getattr(profile, w.lease, None) is None):     # a part of the lease not read
            return "check", f"{note}, so the tenant can look there; the sheet asks: {questions[w.fact]}"
        return "tell", f"the sheet asks: {questions[w.fact]}" + (f"; {note}" if note else "")
    row = clock_rows.get(w.clock)
    clock = next(c for c in playbook.spec.clocks if c.id == w.clock)
    if row is None and clock.applies_if in facts:              # the clock does not apply on the confirmed facts
        return "not met", "the period does not apply on the confirmed facts"
    if row is None or row["status"].startswith("need date"):   # its start date (or applies_if fact) not confirmed
        return "tell", f"the sheet asks: {questions[clock.trigger if row is not None else clock.applies_if]}"
    if row["status"].startswith("not computed"):
        return "outside", row["status"]
    return ("met", "") if row["status"] == (w.equals or "passed") else (otherwise, " ".join(w.when_otherwise.split()))


def option_status(states):
    """An option's status from its gates' states: closed when one is not met, else not known yet while one is the
    tenant's to tell or check, else not settled, outside the tool, not open yet, or open."""
    for state, status in (("not met", "closed"), ("tell", "not known yet"), ("check", "not known yet"),
                          ("not settled", "not settled"), ("outside", "outside the tool"), ("not met yet", "not open yet")):
        if state in states:
            return status
    return "open"


def check_options(playbook, facts, today, profile=None):
    """Each option of the playbook with its status, from the confirmed facts, the clocks, and the lease profile only
    (option_status: open, closed, not known yet, not settled, outside the tool, or not open yet). Each gate takes the best
    state among its ways (STATES): its status and what the tool knows of it (STATUS, KNOWLEDGE), why, its ways with
    theirs, and, while it is not met, if_met: what the option's status would be were it met (were it not met, the
    option is closed). Each step is "done" (its fact confirmed with its value, or its clock's date passed), "waiting"
    (its clock's date upcoming), or "to do". Returns [{"option", "label", "cite", "status", "gates", "steps",
    "also_open"}]."""
    clock_rows = {row["clock"]: row for row in compute_deadlines(playbook, facts, today)}
    results = []
    for o in playbook.spec.options:
        gates = []
        for g in o.gates:
            ways = []
            for w in g.ways:
                state, why = way_state(w, playbook, facts, clock_rows, profile)
                ways.append({"says": w.says or g.says, "cite": w.cite or g.cite, "state": state, "status": STATUS[state],
                             "knowledge": KNOWLEDGE[state], **({"why": why} if why else {})})
            best = min(ways, key=lambda x: STATES.index(x["state"]))
            gates.append({"says": g.says, "cite": g.cite, "state": best["state"], "status": best["status"],
                          "knowledge": best["knowledge"], **({"why": best["why"]} if "why" in best else {}),
                          "ways": ways})
        for i, gate in enumerate(gates):                    # what the option would be were this condition met
            if gate["state"] != "met":
                gate["if_met"] = option_status([x["state"] for j, x in enumerate(gates) if j != i])
        steps = []
        for s in o.steps:
            if s.clock:
                state = {"passed": "done", "upcoming": "waiting"}.get(clock_rows.get(s.clock, {}).get("status"), "to do")
            else:
                state = "done" if facts.get(s.fact) == s.equals else "to do"
            steps.append({"says": s.says, "cite": s.cite, "status": state})
        results.append({"option": o.id, "label": o.label, "cite": o.cite,
                        "status": option_status([gate["state"] for gate in gates]), "gates": gates,
                        "steps": steps, "also_open": list(o.also_open)})
    return results


# ---- Classify and Fill Facts: two one-shot model calls made once at intake. Nothing here is confirmed.

# The issue labels classify can pick. Each gets a playbook (except "other", which means none fits); a playbook
# names the statute sections it rests on in its own `sections`, checked against statutes/ when it loads.
ISSUE_LABELS = [
    "deposit_not_returned",
    "deposit_claim_received",
    "repair_not_made",
    "notice_received_nonpayment",
    "notice_received_violation",
    "landlord_entered_unannounced",
    "rent_increased",
    "wants_to_leave_early",
    "lease_ending",
    "neighbor_disturbance",
    "other",
]


NOT_JSON = "\n\nYour last answer was not valid JSON. Return ONLY the JSON object, nothing else."


def ask_json(llm, prompt, tries=3):
    """Send a prompt, strip any markdown fences, return parsed JSON. An answer that is not valid JSON is asked
    for again with NOT_JSON added, up to `tries` answers in all (in the eval of 2026-10-01, 3 of 51 intakes
    crashed run.py on one); the last failure is raised."""
    for attempt in range(tries):
        raw = llm.invoke(prompt + (NOT_JSON if attempt else "")).content.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            return json.loads(raw, strict=False)          # a line break inside a quoted string is kept, not refused
        except json.JSONDecodeError:
            if attempt == tries - 1:
                raise


def classify(description, menu):
    """Which issue labels fit the tenant's description? Multi-label. menu: every label with the situation it
    covers (corpus.issue_menu()). A label counts only if the tenant says that situation has happened. "other"
    goes with the covered labels when a separate problem fits none of them, so run.py can tell the tenant
    part of it may not be covered (NOT_COVERED); alone, it means nothing fits."""
    labels = "\n".join(f"- {label}: {situation}" for label, situation in menu.items())
    prompt = f"""A Florida residential tenant describes a problem. Each label below covers one situation.
Pick every label whose situation the tenant says has happened. Read who did what: a notice the tenant sent is
not a notice the tenant received. Add "other" when a separate problem the tenant describes fits none of the
situations (for example, a landlord's remark about the tenant's religion next to a broken heater), and use it
alone when nothing fits. A detail of a situation a label covers is part of it, not a separate problem: why it
happened, how it affects the tenant, what the tenant paid or was charged (a partial payment, a receipt, a
late fee), or what a notice says.
Do not guess facts the tenant did not state.
Return ONLY JSON: {{"issues": [...], "reason": "one sentence per label, quoting what the tenant said"}}

LABELS:
{labels}

TENANT SAID:
{description}"""
    result = ask_json(agent_llm, prompt)
    result["issues"] = [i for i in result["issues"] if i in menu]   # drop anything invented
    if not result["issues"]:
        result["issues"] = ["other"]                                  # nothing fits: say so in the record
    return result


def fill_facts(description, playbook):
    """Pull answers out of the description. Each is tagged stated or inferred and must rest on the tenant's
    own words. Nothing here is confirmed; the tenant confirms each one on the intake sheet (sheet.py)."""
    slots = [{"id": e.id, "type": e.type, "question": playbook.guidance["questions"][e.id]}
             for e in playbook.spec.elements if "user" in e.source]
    prompt = f"""Read what the tenant said and answer each question if you can.
Return ONLY a JSON object. For each id: {{"value": ..., "how": "stated" or "inferred", "said": "exact words copied from the tenant"}}.
"stated" means the tenant answered the question directly. "inferred" means the answer follows from what the
tenant said (for example, comparing two dates they gave). Either way, "said" must be the tenant's exact words
that the answer rests on. If nothing the tenant said supports an answer, omit the id.
Rules: date -> "YYYY-MM-DD" only if the tenant gave day, month, and year. bool -> true/false.
money -> number without $ or commas. Never compute a date; only copy one the tenant gave.

QUESTIONS:
{json.dumps(slots, indent=2)}

TENANT SAID:
{description}"""
    answers = ask_json(agent_llm, prompt)

    slot_ids = [s["id"] for s in slots]
    proposed = {}
    for slot_id, a in answers.items():
        said = squash(a.get("said", ""))
        how = a.get("how")
        if slot_id in slot_ids and how in ("stated", "inferred") and said and said in squash(description):
            proposed[slot_id] = {"value": a["value"], "how": how, "basis": a["said"]}
        else:
            print(f"  dropped {slot_id}: no supporting quote or tag")
    return proposed
