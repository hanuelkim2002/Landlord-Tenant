"""Smoke Tests, offline: each block checks one piece without the agent and without a model call, so it runs
with no key. Needs the saved test matter, matters/t-test/test-001/. The model calls are in smoke_online.py.

    python smoke.py
"""
from datetime import date

import record
from corpus import check_all_playbooks, playbooks
from deterministic import check_elements, compute_deadlines
from record import list_matters, load_matter
from timeline import render_timeline
from tools import build_letter

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
