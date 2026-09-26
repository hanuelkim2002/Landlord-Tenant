"""Smoke Tests: each block checks one piece without the agent. Needs a saved lease profile for the matter.

    python smoke.py
"""
import json
from datetime import date

import record
from corpus import check_all_playbooks, playbooks
from deterministic import check_elements, classify, compute_deadlines, fill_facts
from lease import LeaseProfile
from record import matter_dir
from timeline import render_timeline
from tools import build_letter

record.profile = LeaseProfile.model_validate_json((matter_dir() / "lease_profile.json").read_text())
pb = playbooks["deposit_not_returned"]

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

# classifier and slot filling on a description (two model calls)
description = """I rented a house in Gainesville. My lease ended July 31, 2026 and I moved out
and gave the keys back on July 30, 2026. I emailed the property manager my new address the same
day. It's September now and I haven't gotten my $1,850 deposit back or any letter about it."""
print(classify(description))
proposed = fill_facts(description, pb)
print(proposed)
for row in check_elements(pb, record.profile, {}, proposed):
    print(row)
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
