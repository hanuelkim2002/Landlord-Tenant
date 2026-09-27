"""Intake Sheet: the facts a matter still needs, asked by code and saved by code. No model is involved.

Two halves, so a front end can later draw the same rows as a form:
  pending_rows()  which facts need the tenant now, with the question, the type, and any suggested answer
  run_sheet()     asks them in the terminal, one at a time, and saves each answer with record.confirm_fact

Every answer is checked against the element's type before it is saved. A suggestion (from fill_facts) is
shown with the tenant's own words and accepted with Enter. "?" skips a fact for now; it stays missing.
"""
from datetime import datetime

import record
from corpus import playbooks
from record import confirm_fact, element_status, save


# ---- Which rows: every changed, proposed, or missing fact across the matter's issues, once per fact id.

def pending_rows():
    """The facts that need the tenant, in playbook order. Each row: issue, id, type, question, status,
    suggested (a value or None), basis (the tenant's words behind the suggestion), confirmed (for changed)."""
    rows, seen = [], set()
    for issue, statuses in element_status().items():
        pb = playbooks[issue]
        types = {e.id: e.type for e in pb.spec.elements}
        for s in statuses:
            if s["status"] not in ("changed", "proposed", "missing") or s["id"] in seen:
                continue
            seen.add(s["id"])                          # a fact two issues share is asked once
            rows.append({
                "issue": issue, "id": s["id"], "type": types[s["id"]],
                "question": pb.guidance["questions"][s["id"]], "status": s["status"],
                "suggested": s.get("new_value") if s["status"] == "changed" else s.get("value"),
                "basis": s.get("basis"),
                "confirmed": s.get("value") if s["status"] == "changed" else None,
            })
    return rows


# ---- Checking an answer against the element's type.

def parse_answer(kind, text):
    """Turn what the tenant typed into a value of the element's type. Returns (value, None) if it fits,
    or (None, a short message saying what is expected) if it does not."""
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


# ---- Asking: one fact at a time. The list is rebuilt after each answer, so a fact that only applies once
# another is confirmed (applies_if) appears as soon as it does.

HINT = {"date": "YYYY-MM-DD", "bool": "yes/no", "money": "amount", "text": "words"}


def run_sheet(ask=input):
    """Ask every pending fact until none is left or the tenant has skipped the rest. Returns how many were saved.
    ask is the function that reads one answer; input by default, a list's iterator in tests."""
    print("\nFacts for your matter. Enter accepts a suggested answer, or type the right one. ? skips for now.\n")
    skipped, saved, last_issue = set(), 0, None
    while True:
        rows = [r for r in pending_rows() if r["id"] not in skipped]
        if not rows:
            break
        r = rows[0]
        if r["issue"] != last_issue:
            print(f"[{r['issue']}]")
            last_issue = r["issue"]

        # A suggestion is offered only if it fits the type; a malformed one is treated as no suggestion.
        suggested = None
        if r["suggested"] is not None:
            suggested, _ = parse_answer(r["type"], shown(r["suggested"]))
        print(f"  {r['question']} ({HINT[r['type']]})")
        if r["status"] == "changed":
            print(f"    you confirmed: {shown(r['confirmed'])}   your update says: {shown(r['suggested'])}")
        if suggested is not None:
            print(f"    suggested: {shown(suggested)}, from your words: \"{r['basis']}\"")

        answer = ask("    > ").strip()
        if answer == "?":
            skipped.add(r["id"])
            continue
        if answer == "" and suggested is not None:
            value = suggested
        else:
            value, expected = parse_answer(r["type"], answer)
            if expected:
                print(f"    Please type {expected}, or ? to skip.")
                continue

        confirm_fact(r["id"], value, "sheet")
        save(record.matter)
        record.append_transcript({"role": "sheet", "id": r["id"], "question": r["question"],
                                  "typed": answer, "value": value})
        saved += 1

    if skipped:
        print(f"\nSkipped for now: {', '.join(sorted(skipped))}. Deadlines wait until these are answered.")
    return saved
