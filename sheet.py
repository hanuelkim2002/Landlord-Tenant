"""Confirmation: after a turn in which the model proposed facts, the tenant confirms them. Asked and saved by code. No
model is involved. It asks only to confirm what the tenant said, never for a fact the record lacks.

In pieces, so the terminal and the web page (app.py) ask the same rows the same way:
  pending_rows()  what the tenant confirms now: the proposed facts, and a fact whose proposal differs from the confirmed one
  row_notes(r)    the lines shown under a row's label
  value_of(r, a)  the tenant's answer checked against the row's type (an empty answer takes the suggestion)
  save_answer()   saves one answer with record.confirm_fact and transcribes it
  run_sheet()     the terminal's confirmation: asks the rows one at a time with the pieces above

Every answer is checked against the row's type before it is saved. A suggestion (from the model's propose_facts) is shown
with the tenant's own words and accepted with Enter. "?" skips a fact for now; its proposal stays, and it is asked again at
the next confirmation.
"""
from datetime import datetime

import record
from record import confirm_fact, save


# ---- Which rows: every proposed fact, once per fact id, in the order proposed.

def pending_rows():
    """What the tenant confirms now: each fact in matter["proposed"], in the order proposed. Each row: id, label (the id
    in words), type (the type of a clock fact of a loaded skill, record.clock_facts: "date", "bool", or "county"; "text"
    for any other fact), status ("proposed", or "changed" when the id is already confirmed with another value), suggested
    (the proposed value), basis (the tenant's words it came from), and confirmed (the confirmed value of a changed row,
    else None). A fact the record lacks is never a row."""
    types = record.clock_facts()
    facts = record.matter["facts"]
    rows = []
    for fact_id, p in record.matter["proposed"].items():
        changed = fact_id in facts and shown(facts[fact_id]) != shown(p["value"])      # as the tenant reads them
        rows.append({
            "id": fact_id, "label": fact_id.replace("_", " "), "type": types.get(fact_id, "text"),
            "status": "changed" if changed else "proposed", "suggested": p["value"], "basis": p["basis"],
            "confirmed": facts[fact_id] if changed else None,
        })
    return rows


# ---- Checking an answer against the row's type.

def parse_answer(kind, text):
    """Turn what the tenant typed into a value of the row's type. Returns (value, None) if it fits, or (None, a short
    message saying what is expected) if it does not. Types: "date" (2026-07-31 or 7/31/2026), "bool" (yes or no), and
    anything else, "text" or "county", some words."""
    text = text.strip()
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
    if not text:                                       # text, county
        return None, "some words"
    return text, None


def shown(value):
    """How a value reads on the sheet: yes/no for booleans, as is otherwise."""
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return str(value)


# ---- Asking: one row at a time. The list is rebuilt after each answer.

HINT = {"date": "YYYY-MM-DD", "bool": "yes/no", "county": "county name", "text": "words"}


def suggestion(r):
    """A row's suggested value, offered only if it fits the type; a malformed one counts as no suggestion."""
    if r["suggested"] is None:
        return None
    return parse_answer(r["type"], shown(r["suggested"]))[0]


def row_notes(r):
    """The lines shown under a row's label: for a changed fact, what was confirmed and what the tenant's words say now;
    the suggestion with the tenant's words it came from, or just the words when the suggestion does not fit the type."""
    notes = []
    if r["status"] == "changed":
        notes.append(f"was {shown(r['confirmed'])}, now {shown(r['suggested'])}?")
    if suggestion(r) is not None:
        notes.append(f"suggested: {shown(suggestion(r))}, from your words: \"{r['basis']}\"")
    elif r["basis"]:
        notes.append(f"from your words: \"{r['basis']}\"")
    return notes


def value_of(r, answer):
    """The value of the tenant's answer to a row: the suggestion for an empty answer when there is one, else the
    answer parsed by the row's type. Returns (value, None), or (None, what is expected) if it does not fit."""
    if answer == "" and suggestion(r) is not None:
        return suggestion(r), None
    return parse_answer(r["type"], answer)


def save_answer(r, answer, value):
    """Save the answer to one fact row and write it to the transcript: confirmed with record.confirm_fact, matter.json
    saved. Returns the pair to tell the model, (fact id, value)."""
    confirm_fact(r["id"], value, "sheet")
    save(record.matter)
    record.append_transcript({"role": "sheet", "id": r["id"], "label": r["label"], "typed": answer, "value": value})
    return r["id"], value


def skipped_note(fact_ids):
    """What the tenant is told after skipping facts: they stay unconfirmed, and are asked again."""
    names = ", ".join(sorted(i.replace("_", " ") for i in fact_ids))
    return (f"Skipped for now: {names}. They stay unconfirmed, and nothing is counted from an unconfirmed fact. You will "
            "be asked again at the next confirmation.")


def run_sheet(ask=input):
    """The terminal's confirmation: ask every pending fact until none is left or the tenant has skipped the rest. Returns
    what was saved as save_answer's pairs, so the chat loop can tell the model what the tenant decided. ask is the
    function that reads one answer; input by default, a list's iterator in tests."""
    print("\nPlease confirm what you told me. Enter accepts a suggested answer, or type the right one. ? skips for now.\n")
    skipped, saved = set(), []
    while True:
        rows = [r for r in pending_rows() if r["id"] not in skipped]
        if not rows:
            break
        r = rows[0]
        print(f"  {r['label']} ({HINT[r['type']]})")
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
        print("\n" + skipped_note(skipped))
    return saved
