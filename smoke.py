"""Smoke Tests, offline: each check tests one piece without a model call, so it runs with no key. Needs the saved
test matter, matters/t-test/test-001/. The model calls are in smoke_online.py. The checks are in parts, in
smoke_parts/ (split out of this file on 2026-10-06), each run here in order: every line must be OK, like the
skill checks, and the last line says "all checks OK" or lists the failures.

    python smoke.py
"""
from checks import summary

# Each part runs its checks when it is imported, in this order. A part that writes to a matter does it on its own
# throwaway copy of the test matter, removed at its end even after a failure.
import smoke_parts.pieces                    # each piece on its own: no playbook left, deadlines, cases, wiki, cites, quotes
import smoke_parts.writing_to_a_matter       # sessions, propose_facts, the sheet, cites, cases, events, the timeline
import smoke_parts.skills_and_turns          # the model loads skills, old matters, intake and resume; turns with a stand-in model
import smoke_parts.visits                    # visit.py: a new matter, a returning tenant, the confirmation, the record put back; the terminal is gone
import smoke_parts.lease_and_letters         # the rules, the short lease profile and search, deadlines from a message, letters, every skill's clock facts
import smoke_parts.web_page                  # app.py, headless
import smoke_parts.skill_files               # the skill format and its checks, on fixtures in a temporary folder
import smoke_parts.scenarios                # dev/scenarios/ in the conversation format, dev/live_run.py's screen and answer rules, dev/eval.py scoring a run

summary()
