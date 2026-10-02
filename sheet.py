"""Intake Sheet: the facts a matter still needs, asked by code and saved by code. No model is involved.

Two halves, so a front end can later draw the same rows as a form:
  pending_rows()  which facts need the tenant now, with the question, the type, and any suggested answer
  run_sheet()     asks them in the terminal, one at a time, and saves each answer with record.confirm_fact

Every answer is checked against the element's type before it is saved. A suggestion (from fill_facts) is
shown with the tenant's own words and accepted with Enter. "?" skips a fact for now; it stays missing.
"""
import json
from datetime import datetime

import record
from corpus import playbooks
from lease import clauses_about
from record import confirm_fact, confirm_issue, element_status, read_events, reject_issue, save


# ---- Which rows: every changed, proposed, or missing fact across the matter's issues, once per fact id.

def pending_rows():
    """What needs the tenant: first every suggested issue (a yes/no row, kind "issue"), then the facts of the
    active issues in playbook order (kind "fact"). Each row: kind, issue, id, type, question, status,
    suggested (a value or None), basis (the tenant's words behind the suggestion, or why an issue was
    suggested), confirmed (for changed), lease_says (the lease's words, when the lease field named in the
    playbook differs from the suggestion)."""
    rows = [{"kind": "issue", "issue": p["issue"], "id": "issue:" + p["issue"], "type": "bool",
             "question": f"This looks like: {playbooks[p['issue']].description} Is that part of your situation?",
             "status": "suggested", "suggested": None, "basis": p["because"], "confirmed": None, "lease_says": None}
            for p in record.matter["proposed_issues"]]
    seen = set()
    for issue, statuses in element_status().items():
        pb = playbooks[issue]
        types = {e.id: e.type for e in pb.spec.elements}
        for s in statuses:
            if s["status"] not in ("changed", "proposed", "missing") or s["id"] in seen:
                continue
            seen.add(s["id"])                          # a fact two issues share is asked once
            rows.append({
                "kind": "fact", "issue": issue, "id": s["id"], "type": types[s["id"]],
                "question": pb.guidance["questions"][s["id"]], "status": s["status"],
                "suggested": s.get("new_value") if s["status"] == "changed" else s.get("value"),
                "basis": s.get("basis"),
                "confirmed": s.get("value") if s["status"] == "changed" else None,
                "lease_says": s.get("lease_says"),
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
    """Ask every suggested issue and pending fact until none is left or the tenant has skipped the rest.
    Returns what was saved as (id, value) pairs (an issue as ("issue <name>", "confirmed" or "rejected")), so
    the chat loop can tell the model what the tenant decided.
    ask is the function that reads one answer; input by default, a list's iterator in tests."""
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

        # A suggestion is offered only if it fits the type; a malformed one is treated as no suggestion.
        suggested = None
        if r["suggested"] is not None:
            suggested, _ = parse_answer(r["type"], shown(r["suggested"]))
        print(f"  {r['question']} ({HINT[r['type']]})")
        if r["status"] == "changed":
            print(f"    you confirmed: {shown(r['confirmed'])}   your update says: {shown(r['suggested'])}")
        if suggested is not None:
            print(f"    suggested: {shown(suggested)}, from your words: \"{r['basis']}\"")
        if r["lease_says"]:
            print(f"    your lease says: \"{r['lease_says']}\" (shown for comparison; this tool does not decide which is right)")
        if r["kind"] == "issue":
            print(f"    suggested because of: {r['basis']}")

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

        if r["kind"] == "issue":                           # yes: active, its questions follow; no: logged, gone
            (confirm_issue if value else reject_issue)(r["issue"])
            save(record.matter)
            print(f"    {'Its questions follow.' if value else 'Taken out of your matter; logged.'}")
            record.append_transcript({"role": "sheet", "id": r["id"], "question": r["question"],
                                      "typed": answer, "value": value})
            saved.append((f"issue {r['issue']}", "confirmed" if value else "rejected"))
            continue

        suggested_before = [p["issue"] for p in record.matter["proposed_issues"]]
        confirm_fact(r["id"], value, "sheet")              # may suggest a related issue; it is asked next
        save(record.matter)
        added = [p["issue"] for p in record.matter["proposed_issues"] if p["issue"] not in suggested_before]
        for issue in added:
            print(f"    Suggested for your matter: {issue}. It is asked next.")
        record.append_transcript({"role": "sheet", "id": r["id"], "question": r["question"],
                                  "typed": answer, "value": value, **({"issues_suggested": added} if added else {})})
        saved.append((r["id"], value))

    if skipped:
        print(f"\nSkipped for now: {', '.join(sorted(skipped))}. Deadlines wait until these are answered.")
    return saved


# ---- When nothing the tool covers is left: what it does cover, and the parts of the tenant's lease on the
# subject of what they wrote, as printed. No model involved.

STOP_LINE = "None of the situations this tool covers applies, so it stops here. What you described is saved in your matter's record."
CLAUSE_CHARS = 600                                       # a longer clause is cut, marked with "..."


def stop_text():
    """What run.py prints when no covered issue is active: STOP_LINE, the situations the tool covers (each
    playbook's description) and how to come back to one, then the lease clauses lease.clauses_about finds for
    the tenant's description and updates, each with its section, title, and page, word for word."""
    lines = [STOP_LINE, "", "This tool covers these situations:"]
    lines += [f"  - {pb.description}" for pb in playbooks.values()]
    lines += ["If one of them is part of what happened, open this matter again (choose existing) and describe that part."]
    told = " ".join([record.matter.get("description", "")]
                    + [ev["text"] for ev in read_events() if ev["kind"] == "tenant_update"])
    pages = record.matter_dir() / "pages.json"
    found = clauses_about(told, json.loads(pages.read_text())) if pages.exists() else []
    if found:
        lines += ["", "Parts of your lease that may be on the subject, as printed in the lease:"]
        for c in found:
            words = c["text"] if len(c["text"]) <= CLAUSE_CHARS else c["text"][:CLAUSE_CHARS].rsplit(" ", 1)[0] + " ..."
            lines.append(f'  Lease Section {c["number"]}, {c["title"]}, page {c["page"]}: "{words}"')
        lines.append("This tool does not decide what they mean for you.")
    return "\n".join(lines)

