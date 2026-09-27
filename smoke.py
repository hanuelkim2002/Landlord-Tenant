"""Smoke Tests, offline: each block checks one piece without the agent and without a model call, so it runs
with no key. Needs the saved test matter, matters/t-test/test-001/. The model calls are in smoke_online.py.
The last section runs the code that writes to a matter on a throwaway copy and prints named checks: every
line must be OK, like the playbook quote checks.

    python smoke.py
"""
import contextlib
import io
import json
from datetime import date

import record
from checks import check, make_scratch, remove_scratch, summary
from config import MATTERS
from corpus import check_all_playbooks, playbooks
from deterministic import check_elements, compute_deadlines
from record import (append_event, append_transcript, end_session, list_matters, load_matter, matter_dir,
                    new_matter_id, read_events, start_session)
from sheet import pending_rows, run_sheet
from timeline import render_timeline
from tools import build_letter, fact_status, get_deadlines, get_statute_section, propose_facts

load_matter("t-test", "test-001")         # the test matter and its lease profile, from disk
pb = playbooks["deposit_not_returned"]

# listing and loading: every saved matter, then what load_matter put in record
print(list_matters())
print(record.matter["tenant"], record.matter["id"], record.matter["issues"], type(record.profile).__name__)
print()

# playbook quotes against the statute text
check_all_playbooks()
print()

# elements and deadlines with hand-typed facts and a fixed "today"
test_facts = {
    "tenancy_terminated": "2026-07-31",
    "vacated": "2026-07-30",
    "claim_notice_received": False,
    "forwarding_address_given": True,
    "early_or_periodic": False,
}
for row in check_elements(pb, record.profile, test_facts, {}):
    print(row)
print()
for d in compute_deadlines(pb, test_facts, today=date(2026, 9, 8)):
    print(d)
print()

# a later update against confirmed facts: a different value is "changed", the same value stays "known",
# and a value read from the lease is never "changed". get_deadlines waits while a change is open.
update = {
    "claim_notice_received": {"value": True, "how": "stated", "basis": "I got a letter keeping $400"},
    "vacated": {"value": "2026-07-30", "how": "stated", "basis": "July 30, 2026"},
    "deposit_amount": {"value": 1500, "how": "stated", "basis": "$1,500"},
}
for row in check_elements(pb, record.profile, test_facts, update):
    if row["id"] in update:
        print(row)
record.matter["issues"] = ["deposit_not_returned"]
record.matter["facts"] = dict(test_facts)
record.matter["proposed"] = update
print(get_deadlines.invoke({}))
record.matter["proposed"] = {}
print()

# the letter template
record.matter["issues"] = ["deposit_not_returned"]
record.matter["facts"] = dict(test_facts)
print(build_letter("Return the $1,850.00 deposit to 12 Elm St, Gainesville FL 32601", 10, "certified mail, return receipt requested",
                   [{"cite": "Fla. Stat. 83.49(3)(a)", "text": pb.spec.clocks[0].quote}]))
print()

# the record as the tenant sees it, then with the tool's bookkeeping included
print(render_timeline())
print()
print(render_timeline(full=True))
print()


# ---- Code that writes to a matter, on a throwaway copy of the test matter (matters/t-smoke/m-001, removed
# at the end even if a check fails): sessions, propose_facts, the intake sheet, deadlines, events, the
# transcript, and the timeline. Every line must be OK.

def scripted(answers):
    """An ask function for run_sheet that types the given answers in order, and fails loudly if it runs out."""
    answers = iter(answers)
    def ask(prompt):
        return next(answers)
    return ask


def stated(value, words):
    return {"value": value, "how": "stated", "basis": words}


make_scratch("t-smoke",
             issues=["deposit_not_returned", "deposit_claim_received"],
             facts={"tenancy_terminated": "2026-07-31", "claim_notice_received": False},
             proposed={"claim_notice_received": stated(True, "I got a letter from the landlord"),
                       "claim_notice_date": stated("2026-09-25", "on September 25, 2026"),
                       "claim_notice_dated": stated("2026-09-22", "dated September 22, 2026"),
                       "claim_notice_received_on": stated("2026-09-25", "on September 25, 2026"),
                       "claim_delivery": stated("certified mail", "by certified mail"),
                       "claim_amount": stated(400, "keeping $400"),
                       "claim_reason": stated("cleaning", "for cleaning")})
try:
    load_matter("t-smoke", "m-001")
    check("list_matters finds the scratch matter", {"tenant": "t-smoke", "id": "m-001"}.items()
          <= next((m for m in list_matters() if m["tenant"] == "t-smoke"), {}).items())
    check("new_matter_id counts the tenant's matters", new_matter_id("t-smoke") == "m-002")
    events_before = len(read_events())

    sid = start_session("existing")
    check("start_session opens a session", record.session == sid)

    # propose_facts: one suggestion taken, five refused, each for its own reason
    append_transcript({"role": "tenant", "text": "Actually I moved out on July 29, 2026. I never got any letter."})
    said = "I moved out on July 29, 2026"
    reply = propose_facts.invoke({"facts_json": json.dumps({
        "vacated": {"value": "2026-07-29", "how": "stated", "said": said},
        "rent_amount": {"value": 1200, "how": "stated", "said": said},
        "forwarding_address_given": {"value": True, "how": "stated", "said": "I told them by phone"},
        "early_or_periodic": {"value": "not sure", "how": "stated", "said": said},
        "objected": {"value": False, "how": "guessed", "said": said},
        "tenancy_terminated": {"value": "2026-07-31", "how": "stated", "said": said},
    })})
    check("propose_facts takes a well-formed suggestion", "Suggested: vacated." in reply)
    check("propose_facts refuses a fact the issues do not ask for", "rent_amount: not a fact" in reply)
    check("propose_facts refuses words the tenant never typed", "forwarding_address_given: said must be" in reply)
    check("propose_facts refuses a value of the wrong type", "early_or_periodic: value must be yes or no" in reply)
    check("propose_facts refuses a how other than stated or inferred", "objected: how must be" in reply)
    check("propose_facts refuses a value already confirmed", "tenancy_terminated: already confirmed" in reply)
    check("propose_facts never confirms", "vacated" not in record.matter["facts"])
    check("get_deadlines waits while facts are open", get_deadlines.invoke({}).startswith("Not yet"))

    # the intake sheet: accept, correct, bad input asked again, a changed fact, an applies_if fact, a skip
    with contextlib.redirect_stdout(io.StringIO()):
        saved = run_sheet(scripted(["", "maybe", "", "", "y", "no", "", "", "", "$1,2x", "400", "", "?", "no"]))
    facts = record.matter["facts"]
    check("sheet saves every answered fact", len(saved) == 11)
    check("sheet: Enter accepts a suggestion", facts["vacated"] == "2026-07-29")
    check("sheet: a changed fact takes the new value", facts["claim_notice_received"] is True)
    check("sheet: an applies_if fact is asked once it applies", facts.get("claim_notice_date") == "2026-09-25")
    check("sheet: a bad amount is asked again, then saved", facts["claim_amount"] == 400)
    check("sheet: yes/no answers are saved as true/false", facts["forwarding_address_given"] is True
          and facts["early_or_periodic"] is False)
    check("sheet: a skipped fact stays open", [r["id"] for r in pending_rows()] == ["notice_states_objection_window"])
    with contextlib.redirect_stdout(io.StringIO()):
        run_sheet(scripted(["yes"]))
    deadlines = {d["clock"]: str(d.get("deadline")) for d in json.loads(get_deadlines.invoke({}))}
    check("get_deadlines answers once every fact is confirmed", deadlines.get("tenant_objection_deadline") == "2026-10-10")
    check("fact_status shows a confirmed fact as known", any(r["id"] == "vacated" and r["status"] == "known"
          for r in json.loads(fact_status.invoke({}))["deposit_not_returned"]))

    # events and the transcript
    append_event("tenant_update", text="The landlord emailed me again today about the cleaning charge.")
    end_session()
    check("end_session closes the session", record.session is None)
    get_statute_section.invoke({"section": "83.49"})          # after the session: must carry no session id
    new_events = read_events()[events_before:]
    in_session = [e for e in new_events if e["kind"] != "fetch"]
    confirmations = [e for e in new_events if e["kind"] == "fact_confirmed"]
    check("every event in the session carries its id", all(e.get("session") == sid for e in in_session))
    check("an event after the session carries no id", "session" not in new_events[-1])
    check("session_started and session_ended are logged", in_session[0]["kind"] == "session_started"
          and in_session[-1]["kind"] == "session_ended")
    check("every fact is confirmed on the sheet", len(confirmations) == 12
          and all(e["confirmed_in"] == "sheet" for e in confirmations))
    lines = [json.loads(line) for line in (matter_dir() / "sessions" / f"{sid}.jsonl").read_text().splitlines()]
    check("the transcript holds the tenant's words and every sheet answer",
          [line["role"] for line in lines].count("tenant") == 1 and [line["role"] for line in lines].count("sheet") == 12)

    # the timeline
    full, plain = render_timeline(full=True), render_timeline()
    check("timeline full shows the session with its transcript", f"session {sid[:8]} started" in full
          and f"sessions/{sid}.jsonl" in full)
    check("the plain timeline leaves sessions out", "session" not in plain)
    check("the timeline shows a tenant update", "tenant update: The landlord emailed me again" in plain)
    check("the timeline keeps same-day events in log order",
          full.index(f"session {sid[:8]} started") < full.index(f"session {sid[:8]} ended"))
finally:
    remove_scratch("t-smoke")
check("the scratch matter is removed", not (MATTERS / "t-smoke").exists())
summary()
