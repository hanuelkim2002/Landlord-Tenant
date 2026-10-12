"""Intake Sheet: the facts a matter still needs, asked by code and saved by code. No model is involved.

In pieces, so the terminal and the web page (app.py) ask the same rows the same way:
  pending_rows()  which facts need the tenant now, with the question, the type, and any suggestion
  row_notes(r)    the lines shown under a row's question
  value_of(r, a)  the tenant's answer checked against the row's type (an empty answer takes the suggestion)
  save_answer()   saves one answer with record.confirm_fact and transcribes it
  run_sheet()     the terminal's sheet: asks the rows one at a time with the pieces above

Every answer is checked against the element's type before it is saved. A suggestion (from the model's propose_facts)
is shown with the tenant's own words and accepted with Enter. "?" skips a fact for now; it stays missing.
"""
from datetime import datetime

import record
from config import squash
from corpus import fact_lease, playbooks
from lease import LABELS, lease_cite
from record import confirm_fact, element_status, save


# ---- Which rows: every changed, proposed, or missing fact across the matter's loaded skills, once per fact id.

def pending_rows():
    """What needs the tenant: the facts of the loaded skills' playbooks, in the order the skills were loaded (kind
    "fact"). Each row: kind, issue (the skill's name), id, type, choices (a choice fact's answers), question, status,
    suggested (a value or None), basis (the tenant's words behind the suggestion), confirmed (for changed), lease_says
    (the lease's words, when the lease field named in the playbook differs from the suggestion), lease_clause (the
    lease clause the question is about, corpus.fact_lease, or None; TODO item 81)."""
    rows = []
    seen = set()
    for issue, statuses in element_status().items():
        pb = playbooks[issue]
        elements = {e.id: e for e in pb.spec.elements}
        for s in statuses:
            if s["status"] not in ("changed", "proposed", "missing") or s["id"] in seen:
                continue
            seen.add(s["id"])                          # a fact two issues share is asked once
            rows.append({
                "kind": "fact", "issue": issue, "id": s["id"], "type": elements[s["id"]].type,
                "choices": elements[s["id"]].choices,
                "question": pb.guidance["questions"][s["id"]], "status": s["status"],
                "suggested": s.get("new_value") if s["status"] == "changed" else s.get("value"),
                "basis": s.get("basis"),
                "confirmed": s.get("value") if s["status"] == "changed" else None,
                "lease_says": s.get("lease_says"),
                "lease_clause": fact_lease.get(s["id"]),
            })
    return rows


# ---- Checking an answer against the element's type.

def parse_answer(kind, text, choices=None):
    """Turn what the tenant typed into a value of the element's type. Returns (value, None) if it fits,
    or (None, a short message saying what is expected) if it does not. A choice is answered by its number in the
    list or by its words (spacing and capitals aside), and saved as its words."""
    text = text.strip()
    if kind == "choice":
        if text.isdigit() and 1 <= int(text) <= len(choices):
            return choices[int(text) - 1], None
        named = [c for c in choices if squash(c) == squash(text)]
        return (named[0], None) if named else (None, "a number from the list, or its words")
    if kind == "date":
        for fmt in ("%Y-%m-%d", "%m/%d/%Y"):           # 2026-07-31 or 7/31/2026
            try:
                return datetime.strptime(text, fmt).date().isoformat(), None
            except ValueError:
                pass
        return None, "a date like 2026-07-31 or 7/31/2026"
    if kind == "bool":
        if text.lower() in ("yes", "y", "true"):
            return True, None
        if text.lower() in ("no", "n", "false"):
            return False, None
        return None, "yes or no"
    if kind == "money":
        try:
            amount = float(text.replace("$", "").replace(",", ""))
        except ValueError:
            return None, "an amount like 1850 or $1,850.00"
        return (int(amount) if amount == int(amount) else amount), None
    if not text:                                       # text
        return None, "some words"
    return text, None


def shown(value):
    """How a value reads on the sheet: yes/no for booleans, as is otherwise."""
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return str(value)


# ---- Asking: one row at a time. The list is rebuilt after each answer, so a fact that only applies once
# another is confirmed (applies_if) appears as soon as it does.

HINT = {"date": "YYYY-MM-DD", "bool": "yes/no", "money": "amount", "text": "words", "choice": "number or words"}


def suggestion(r):
    """A row's suggested value, offered only if it fits the type (for a choice, one of its answers); a malformed one
    counts as no suggestion."""
    if r["suggested"] is None:
        return None
    return parse_answer(r["type"], shown(r["suggested"]), r.get("choices"))[0]


def clause_note(field):
    """The lease clause a question is about, for the sheet (TODO item 81): its words as the tool read them, with
    the cite; or that the tool's reading found no such clause, or did not read that part of the lease, so the tenant
    checks the lease itself."""
    clause = getattr(record.profile, field, None) if record.profile is not None else None
    if clause is None:
        return f"the tool has not read the part of your lease on {LABELS[field]}: check your lease itself"
    if not clause.present:
        return f"the tool's reading of your lease found no clause on {LABELS[field]}; check your lease itself"
    return f"your lease's clause on {LABELS[field]} ({lease_cite(clause)}), as the tool read it: \"{' '.join(clause.quote.split())}\""


def row_notes(r):
    """The lines shown under a row's question: a confirmed value next to the update's, the suggestion with the
    tenant's words it came from, the lease's words where they differ, and the lease clause the question is about
    (clause_note)."""
    notes = []
    if r["status"] == "changed":
        notes.append(f"you confirmed: {shown(r['confirmed'])}   your update says: {shown(r['suggested'])}")
    if suggestion(r) is not None:
        notes.append(f"suggested: {shown(suggestion(r))}, from your words: \"{r['basis']}\"")
    if r["lease_says"]:
        notes.append(f"your lease says: \"{r['lease_says']}\" (shown for comparison; this tool does not decide which is right)")
    if r.get("lease_clause"):
        notes.append(clause_note(r["lease_clause"]))
    return notes


def value_of(r, answer):
    """The value of the tenant's answer to a row: the suggestion for an empty answer when there is one, else the
    answer parsed by the row's type. Returns (value, None), or (None, what is expected) if it does not fit."""
    if answer == "" and suggestion(r) is not None:
        return suggestion(r), None
    return parse_answer(r["type"], answer, r.get("choices"))


def save_answer(r, answer, value):
    """Save the answer to one fact row and write it to the transcript: confirmed with record.confirm_fact, matter.json
    saved. Returns the pair to tell the model, (fact id, value)."""
    confirm_fact(r["id"], value, "sheet")
    save(record.matter)
    record.append_transcript({"role": "sheet", "id": r["id"], "question": r["question"], "typed": answer, "value": value})
    return r["id"], value


def run_sheet(ask=input):
    """The terminal's sheet: ask every pending fact until none is left or the tenant has skipped the rest. Returns
    what was saved as save_answer's pairs, so the chat loop can tell the model what the tenant decided. ask is the
    function that reads one answer; input by default, a list's iterator in tests."""
    print("\nFacts for your matter. Enter accepts a suggested answer, or type the right one. ? skips for now.\n")
    skipped, saved, last_issue = set(), [], None
    while True:
        rows = [r for r in pending_rows() if r["id"] not in skipped]
        if not rows:
            break
        r = rows[0]
        if r["issue"] != last_issue:
            print(f"[{r['issue']}]")
            last_issue = r["issue"]
        print(f"  {r['question']} ({HINT[r['type']]})")
        for number, words in enumerate(r.get("choices") or [], 1):     # a choice's answers, to pick by number
            print(f"    {number}. {words}")
        for line in row_notes(r):
            print("    " + line)

        answer = ask("    > ").strip()
        if answer == "?":
            skipped.add(r["id"])
            continue
        value, expected = value_of(r, answer)
        if expected:
            print(f"    Please type {expected}, or ? to skip.")
            continue
        saved.append(save_answer(r, answer, value))

    if skipped:
        print(f"\nSkipped for now: {', '.join(sorted(skipped))}. Deadlines wait until these are answered.")
    return saved
