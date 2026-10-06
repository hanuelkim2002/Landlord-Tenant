"""Smoke Tests, offline: each check tests one piece without a model call, so it runs with no key. Needs the saved
test matter, matters/t-test/test-001/. The model calls are in smoke_online.py. The checks are in parts, in
smoke_parts/ (split out of this file on 2026-10-06), each run here in order: every line must be OK, like the
playbook quote checks, and the last line says "all checks OK" or lists the failures.

    python smoke.py
"""
from checks import summary

# Each part runs its checks when it is imported, in this order. A part that writes to a matter does it on its own
# throwaway copy of the test matter, removed at its end even after a failure.
import smoke_parts.pieces                    # each piece on its own: playbooks, deadlines, cases, wiki, cites, quotes
import smoke_parts.writing_to_a_matter       # sessions, propose_facts, the sheet, cites, cases, events, the timeline
import smoke_parts.issues_and_turns          # issues suggested and dropped; turns with a stand-in model
import smoke_parts.playbooks_options_lease   # every playbook, options and what the tool knows, the lease search
import smoke_parts.web_page                  # app.py, headless

summary()
