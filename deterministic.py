"""Deterministic Layer: element status and date arithmetic (no model), plus the two one-shot intake calls."""
import json
import re
from datetime import date, datetime, timedelta


from calendars import court_calendar, holidays_in
from config import agent_llm, squash


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
        out.append({
            "clock": c.id,
            "actor": c.actor,
            "from": f"{c.trigger} {start}",
            "rule": f"{c.days} {'court business days' if c.count == 'court_business_days' else 'days'} {c.direction}",
            "deadline": deadline,
            "status": "passed" if deadline < today else "upcoming",
            "cite": c.cite,
            "counting": counting,
        })
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
    "other",
]


def ask_json(llm, prompt):
    """Send a prompt, strip any markdown fences, return parsed JSON."""
    raw = llm.invoke(prompt).content.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw)


def classify(description):
    """Which issue labels fit the tenant's description? Multi-label. 'other' is allowed."""
    prompt = f"""A Florida residential tenant describes a problem. Pick every label that fits.
Labels: {ISSUE_LABELS}
Use "other" if nothing fits. Do not guess facts the tenant did not state.
Return ONLY JSON: {{"issues": [...], "reason": "one sentence per label, quoting what the tenant said"}}

TENANT SAID:
{description}"""
    result = ask_json(agent_llm, prompt)
    result["issues"] = [i for i in result["issues"] if i in ISSUE_LABELS]   # drop anything invented
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
