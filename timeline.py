"""Timeline: the record as the tenant sees it. Not a tool. The chat loop prints this directly when the
tenant asks for a timeline, so the record never passes through the model."""
import re
from datetime import date

import record
from deterministic import compute_deadlines
from record import active_playbooks, read_events


def label(ident):
    """'tenancy_terminated' -> 'tenancy terminated'. Used for element and clock ids."""
    return ident.replace("_", " ")


def confirmation_of(fact_id, events):
    """How and when the tenant confirmed a fact, from the last fact_confirmed event for it."""
    for ev in reversed(events):
        if ev["kind"] == "fact_confirmed" and ev["id"] == fact_id:
            return f"tenant ({ev['how']}, confirmed {ev['when'][:10]})"
    return "tenant"


def render_timeline(issue=None, full=False):
    """One dated table for the matter: DATE, EVENT, SOURCE, FILE. Oldest first. Built from the record,
    never from the model. issue=<name> keeps only that issue's deadlines and tagged events, plus everything
    untagged. full=True adds the tool's own bookkeeping (facts confirmed, statute lookups, computations)."""
    events = read_events()
    facts = record.matter["facts"]
    rows = []                                              # (date, event, source, file)
    dates_shown = set()

    for pb in active_playbooks():
        if issue and pb.issue != issue:
            continue
        for e in pb.spec.elements:                         # real-world dates the tenant confirmed
            if e.type == "date" and e.id in facts and e.id not in dates_shown:
                dates_shown.add(e.id)
                rows.append((facts[e.id], label(e.id), confirmation_of(e.id, events), ""))
        for d in compute_deadlines(pb, facts, date.today()):
            if "deadline" in d:
                rows.append((str(d["deadline"]), f"[{pb.issue}] {d['actor']} deadline: {label(d['clock'])}",
                             f"computed, {d['cite']}, {d['status']}", ""))

    for ev in events:
        if issue and ev.get("issue") not in (None, issue):
            continue
        day = ev.get("sent_on", ev["when"][:10])           # a message sorts by its own date, not the day it was recorded
        if ev["kind"] == "communication":
            source = "tenant reported" if ev["sender"].lower() == "tenant" else "tenant pasted"
            draft = re.search(r"draft_\S+\.txt", ev.get("text", ""))     # a sent letter names its draft file
            rows.append((day, f"{ev['channel']} from {ev['sender']} to {ev['recipient']}", source, draft.group() if draft else ""))
        elif ev["kind"] == "artifact":
            rows.append((day, ev["note"], "tenant provided", f"{ev['sha256'][:12]}_{ev['file']}"))
        elif ev["kind"] == "tenant_update":
            text = " ".join(ev["text"].split())
            rows.append((day, "tenant update: " + text[:48] + ("..." if len(text) > 48 else ""), "tenant typed", ""))
        elif ev["kind"] == "draft":
            rows.append((day, f"letter drafted, {ev['posture']} posture", "tool, from confirmed facts", ev["file"]))
        elif full and ev["kind"] == "fact_confirmed":
            basis = (ev.get("basis") or "")[:50] + ("..." if len(ev.get("basis") or "") > 50 else "")
            source = f"{ev['how']}, basis: {basis}" if basis else ev["how"]
            rows.append((day, f"fact confirmed: {label(ev['id'])} = {ev['value']}", source, ""))
        elif full and ev["kind"] == "fetch":
            what = f"read statute {ev['section']}" if "section" in ev else f"searched statute for '{ev['search']}'"
            rows.append((day, what, "tool", ""))
        elif full and ev["kind"] == "session_started":
            rows.append((day, f"session {ev['session'][:8]} started ({ev['how']} matter)", "tool",
                         f"sessions/{ev['session']}.jsonl"))            # the transcript of this session
        elif full and ev["kind"] == "session_ended":
            rows.append((day, f"session {ev['session'][:8]} ended", "tool", ""))
        elif full and ev["kind"] == "deadlines_computed":
            rows.append((day, "computed deadlines: " + ", ".join(label(c) for c in ev["clocks"]), "tool", ""))

    rows.sort(key=lambda row: row[0])                     # by date only; within a day, rows keep the order
                                                           # they were added, so events stay in log order
    lines = [f"{'DATE':<12} {'EVENT':<64} {'SOURCE':<44} FILE"]
    for day, what, source, file in rows:
        lines.append(f"{day:<12} {what:<64} {source:<44} {file}")
    return "\n".join(lines)
