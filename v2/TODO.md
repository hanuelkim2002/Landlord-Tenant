# TODO

Work Claude can do, in order. Each item is at most three lines. Decisions and sign-offs are in AUTHOR.md; model
mistakes are in SLIPS.md.

## Now: the first build (proposed 2026-10-20, awaiting the author's OK)

1. `config.py`, `requirements.txt`, `setup.sh`: paths, the key from `.env`, `AGENT_MODEL` (default nemotron), the
   vision model (Gemma 4), the gateway client. v2 gets its own `venv/`. About 30 lines.
2. `skills/deposit_not_returned.md` in format A, open questions and `count_days` calls inside their conditions, from
   `comparisons/skills/versions/A_checklist.md`. `law.py`: statutes, skills, the skill quote checker. About 90 lines.
3. `record.py`: matter folders, `matter.json`, `events.jsonl` (messages too), pending and confirmed facts;
   `confirm_fact` is the only code that confirms one. About 110 lines.
4. `lease.py`: PyMuPDF reads the PDF; Gemma 4 reads any page without usable text; the pages are stored in the
   matter. About 60 lines.
5. `checks.py`: every quotation of 20+ characters checked against the section it cites or the lease; the cited
   words to print under the reply. About 80 lines.
6. `tools.py`: `get_statute_section`, `search_statute`, `load_skill`, `count_days`, `note_fact`. About 100 lines.
7. `chat.py`: the system prompt (rules 1 to 8, lease rules 1 to 4, the lease, the facts, the skills) and the tool
   loop, which also runs tool calls nemotron writes as text. About 120 lines.
8. `app.py`: the Streamlit page: start or open a matter, the chat with its checks and cited words, pending facts in
   the sidebar with Confirm and a way to correct. About 160 lines.
9. `tests.py`: the quote checker, the skill quote checker, `count_days` cases; no model call. About 100 lines.
10. DOCUMENTATION.md, CLAUDE.md (running), the launch config; then `python tests.py`, and a test matter on the page.

## Later

- Rewrite the other nine skills in format A, after the author has tried `deposit_not_returned` and approves.
- Read pages without usable text in parallel, so a long scanned lease is not read one page at a time.
