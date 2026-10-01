"""Timeline: the record as the tenant sees it. Not a tool. The chat loop prints this directly when the
tenant asks for a timeline, and prints get_deadlines' result with render_deadlines, so the record never
passes through the model."""
import json
import re
from datetime import date

import record
from deterministic import matter_deadlines
from record import active_playbooks, read_events
from sheet import shown


def label(ident):
    """'tenancy_terminated' -> 'tenancy terminated'. Used for element and clock ids."""
    return ident.replace("_", " ")


def corrected(ev):
    """True if the tenant confirmed a different value from the one suggested. Compared as shown, so 400 and
    "400" are the same answer."""
    return ev.get("proposed_value") is not None and shown(ev["proposed_value"]) != shown(ev["value"])


def confirmation_of(fact_id, events):
    """How and when the tenant confirmed a fact, from the last fact_confirmed event for it."""
    for ev in reversed(events):
        if ev["kind"] == "fact_confirmed" and ev["id"] == fact_id:
            how = "corrected" if corrected(ev) else ev["how"]
            return f"tenant ({how}, confirmed {ev['when'][:10]})"
    return "tenant"


def render_deadlines(result):
    """get_deadlines' result as the tenant reads it. The chat loop prints this itself after a turn in which the
    model called get_deadlines, so no part of a deadline depends on the model reporting it: each row shows its
    date, whose deadline, the rule and what it counts from, the cite, the status, the counting line, and its
    issues; a clock with no date shows why. With no deadline at all (an issue with no clocks, or none that
    applies), it says so in one line instead of printing an empty heading. Then the issues still waiting,
    with the facts they wait for."""
    if result.startswith("Not yet."):                      # no issue ready: the waiting list is JSON at the end
        waiting = json.loads(result.split(": ", 1)[1])
        lines = ["No deadlines yet: no issue has all its facts confirmed."]
    else:
        data = json.loads(result)
        waiting = data.get("waiting", {})
        lines = ["Deadlines, computed by the tool from your confirmed facts:" if data["deadlines"] else
                 "No deadlines: none of the deadlines this tool computes applies to your confirmed facts."]
        for d in data["deadlines"]:
            issues = ", ".join(d["issues"])
            if "deadline" not in d:
                lines.append(f"  (no date)   {label(d['clock'])} [{issues}]: {d['status']}")
                continue
            lines.append(f"  {d['deadline']}  {d['actor']} deadline: {label(d['clock'])} [{issues}], {d['status']}")
            lines.append(f"              {d['rule']} {label(d['from'])}, Fla. Stat. {d['cite']}")
            lines.append(f"              counting: {d['counting']}")
            if "shown_with" in d:                          # a confirmed date shown beside the computed one
                lines.append(f"              beside it, from your record: {label(d['shown_with'])}")
    for issue, fact_ids in waiting.items():
        lines.append(f"  waiting [{issue}]: {', '.join(label(f) for f in fact_ids)}")
    return "\n".join(lines)


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

    for d in matter_deadlines(active_playbooks(), facts, date.today()):   # a shared deadline once, both issues
        if "deadline" in d and (not issue or issue in d["issues"]):
            rows.append((str(d["deadline"]), f"[{', '.join(d['issues'])}] {d['actor']} deadline: {label(d['clock'])}",
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
            how = f"corrected from {ev['how']} {shown(ev['proposed_value'])}" if corrected(ev) else ev["how"]
            source = f"{how}, basis: {basis}" if basis else how
            rows.append((day, f"fact confirmed: {label(ev['id'])} = {ev['value']}", source, ""))
        elif full and ev["kind"] == "fetch":
            what = f"read statute {ev['section']}" if "section" in ev else f"searched statute for '{ev['search']}'"
            rows.append((day, what, "tool", ""))
        elif full and ev["kind"] == "issue_added":
            rows.append((day, f"issue added: {label(ev['issue'])}", f"{ev['source']}, {ev['because']}", ""))
        elif full and ev["kind"] == "issue_proposed":
            rows.append((day, f"issue suggested: {label(ev['issue'])}", f"{ev['source']}, {ev['because']}", ""))
        elif full and ev["kind"] in ("issue_confirmed", "issue_rejected", "issue_dropped"):
            what = ev["kind"].removeprefix("issue_")
            where = "tenant, in the chat" if what == "dropped" else "tenant, on the sheet"
            rows.append((day, f"issue {what}: {label(ev['issue'])}", where, ""))
        elif full and ev["kind"] == "session_started":
            rows.append((day, f"session {ev['session'][:8]} started ({ev['how']} matter)", "tool",
                         f"sessions/{ev['session']}.jsonl"))            # the transcript of this session
        elif full and ev["kind"] == "session_ended":
            rows.append((day, f"session {ev['session'][:8]} ended", "tool", ""))
        elif full and ev["kind"] == "reply_empty":
            rows.append((day, "the model's reply was empty; asked again" + ("" if ev["recovered"] else ", still empty"),
                         "tool, agent.retry_empty", ""))
        elif full and ev["kind"] == "cite_flagged":
            rows.append((day, f"a reply's cite flagged: {ev['cite']}", "tool, citations.check_cites", ""))
        elif full and ev["kind"] == "quote_flagged":
            words = ev["quote"].split()
            rows.append((day, "a reply's quote flagged: \"" + " ".join(words[:5]) + ("...\"" if len(words) > 5 else "\""),
                         "tool, citations.check_quoted", ""))
        elif full and ev["kind"] == "cases_shown":
            rows.append((day, f"showed cases on {ev['topic']} ({len(ev['cases'])})" + (", unverified pages" if ev.get("unverified") else ""),
                         "tool, get_cases", ""))
        elif full and ev["kind"] == "deadlines_computed":
            rows.append((day, "computed deadlines: " + ", ".join(label(c) for c in ev["clocks"]), "tool", ""))

    rows.sort(key=lambda row: row[0])                     # by date only; within a day, rows keep the order
                                                           # they were added, so events stay in log order
    lines = [f"{'DATE':<12} {'EVENT':<64} {'SOURCE':<44} FILE"]
    for day, what, source, file in rows:
        lines.append(f"{day:<12} {what:<64} {source:<44} {file}")
    return "\n".join(lines)
