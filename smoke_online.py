"""Smoke Tests, online: the two one-shot intake calls on a sample description. Two model calls, needs the key.
Needs the saved test matter, matters/t-test/test-001/. The offline checks are in smoke.py.

    python smoke_online.py
"""
from config import require_key
require_key()                   # this script calls the model; stop here if the key is missing

import record
from corpus import playbooks
from deterministic import check_elements, classify, fill_facts
from record import load_matter

load_matter("t-test", "test-001")         # the test matter and its lease profile, from disk
pb = playbooks["deposit_not_returned"]

# classifier and slot filling on a description (two model calls)
description = """I rented a house in Gainesville. My lease ended July 31, 2026 and I moved out
and gave the keys back on July 30, 2026. I emailed the property manager my new address the same
day. It's September now and I haven't gotten my $1,850 deposit back or any letter about it."""
print(classify(description))
proposed = fill_facts(description, pb)
print(proposed)
for row in check_elements(pb, record.profile, {}, proposed):
    print(row)
