"""Smoke, part: code that writes to a matter, on a throwaway copy of the test matter (matters/t-smoke/m-001):
listing and ids, sessions, propose_facts, the confirmation, deadlines, YOUR FACTS, a reply's cites, cases through
get_cases, the rules that apply only sometimes, events and the transcript, and the timeline.
Run by smoke.py, in order; each check prints a line, OK or FAIL."""
import contextlib
import io
import json
import re
import shutil
import tempfile
from datetime import date
from pathlib import Path
from langchain.messages import AIMessage, HumanMessage, ToolMessage
import record
from checks import check, make_scratch, remove_scratch
from citations import check_case_cites, check_quoted
from config import MATTERS, WIKI
import wiki
from wiki import verify
from record import (append_event, append_transcript, end_session, list_matters, load_matter, matter_dir,
                    new_matter_id, read_events, start_session)
from sheet import pending_rows, row_notes, run_sheet
from timeline import render_deadlines, render_timeline
from prompt import CASE_RULE, LETTER_RULE, NO_CASES_RULE, PARTS, system_prompt
from replies import CITED_HEAD, check_reply, cited_words, given_text, printed_cases, sections_shown
from agent import turn_blocks
from tools import (deadline_listing, get_cases, get_deadlines, get_statute_section, not_in_record, offered_topics,
                   propose_facts, topic_named)
from tools import tools as model_tools
from smoke_parts.common import FORFEIT, prompt_part, screen, scripted, stated

# ---- Code that writes to a matter, on a throwaway copy of the test matter (matters/t-smoke/m-001, removed
# at the end even if a check fails): sessions, propose_facts, the confirmation, deadlines, YOUR FACTS, events, the
# transcript, and the timeline. Every line must be OK.

make_scratch("t-smoke",
             skills=["deposit_not_returned", "deposit_claim_received"],
             facts={"claim_notice_received": False, "deposit_amount": 1850},          # confirmed before: a yes/no and a number
             proposed={"tenancy_terminated": stated("2026-07-31", "My lease ended July 31, 2026"),
                       "claim_notice_received": stated(True, "I got a letter from the landlord"),
                       "claim_notice_date": stated("2026-09-25", "on September 25, 2026"),
                       "claim_notice_dated": stated("2026-09-22", "dated September 22, 2026"),
                       "claim_delivery": stated("certified mail", "by certified mail"),
                       "claim_reason": stated("cleaning", "for cleaning")})
try:
    load_matter("t-smoke", "m-001")
    check("list_matters finds the scratch matter", {"tenant": "t-smoke", "id": "m-001"}.items()
          <= next((m for m in list_matters() if m["tenant"] == "t-smoke"), {}).items())
    check("new_matter_id counts the tenant's matters", new_matter_id("t-smoke") == "m-002")
    events_before = len(read_events())

    sid = start_session("existing")
    check("start_session opens a session", record.session == sid)
    check("item 112: the loaded skills' clock facts are typed by the role they play, merged",
          record.clock_facts() == {"tenancy_terminated": "date", "vacated": "date", "early_or_periodic": "bool",
                                   "claim_notice_date": "date", "claim_notice_dated": "date"})
    at_start = json.loads(deadline_listing())
    check("item 112: nothing is dated from a proposed fact, and waiting lists each loaded skill's clock facts not confirmed",
          at_start["deadlines"] == [] and at_start["waiting"] == {
              "deposit_not_returned": ["tenancy_terminated", "vacated", "early_or_periodic"],
              "deposit_claim_received": ["tenancy_terminated", "claim_notice_date", "claim_notice_dated"]})
    check("item 46: while facts are open, the prompt's deadline status says what each skill waits for",
          "- waiting [deposit not returned]: no deadline until these are confirmed: tenancy terminated, vacated, early or "
          "periodic" in prompt_part("deadlines"))
    check("printed deadlines say none yet, and what is waiting",
          render_deadlines(deadline_listing()).startswith("No deadlines yet")
          and "waiting [deposit_not_returned]: tenancy terminated, vacated, early or periodic" in render_deadlines(deadline_listing()))

    # propose_facts (item 112): a clock fact of a loaded skill is parsed by its type; any other fact is a name in
    # lowercase words with a plain-text value; each refusal has its own reason
    append_transcript({"role": "tenant", "text": "Actually I moved out on July 29, 2026. I never got any letter. I moved in on "
                       "August 1, 2025. The landlord said he would send a check next week."})
    said = "I moved out on July 29, 2026"
    reply = propose_facts.invoke({"facts_json": json.dumps({
        "vacated": {"value": "2026-07-29", "how": "stated", "said": said},
        "claim_notice_date": {"value": "next Tuesday", "how": "stated", "said": said},
        "early_or_periodic": {"value": "not sure", "how": "stated", "said": said},
        "landlord_response": {"value": "said he would send a check next week", "how": "stated",
                              "said": "The landlord said he would send a check next week"},
        "move_in_date": {"value": "2025-08-01", "how": "stated", "said": "I moved in on August 1, 2025"},
        "Rent Amount": {"value": "1200", "how": "stated", "said": said},
        "a_fact_name_that_is_far_too_long_to_be_kept": {"value": "x", "how": "stated", "said": said},
        "rent_amount": {"value": "1200", "how": "stated", "said": "I pay $1,200 a month"},
        "objected": {"value": "no", "how": "guessed", "said": said},
        "claim_notice_received": {"value": False, "how": "stated", "said": "I never got any letter"},
        "premises_county": {"value": "Alachua", "how": "stated", "said": said},
        "long_story": {"value": "x" * 301, "how": "stated", "said": said},
    })})
    proposed_now = record.matter["proposed"]
    check("item 112: propose_facts takes a clock fact of a loaded skill, parsed by its type (a date)",
          "Proposed: vacated, landlord_response, move_in_date." in reply
          and proposed_now["vacated"] == {"value": "2026-07-29", "how": "stated", "basis": said})
    check("item 112: propose_facts refuses a malformed clock fact: a bad date, a bad yes/no; the earlier proposal stays",
          "claim_notice_date: value must be a date like 2026-07-31 or 7/31/2026" in reply
          and "early_or_periodic: value must be yes or no" in reply and proposed_now["claim_notice_date"]["value"] == "2026-09-25")
    check("item 112: propose_facts takes any other fact as plain text under a name in lowercase words",
          proposed_now["landlord_response"]["value"] == "said he would send a check next week"
          and proposed_now["move_in_date"]["value"] == "2025-08-01")
    check("item 112: propose_facts refuses a bad name (capitals and a space, too long) and a name a skill not loaded counts from",
          "Rent Amount: a fact name is lowercase words joined by underscores, at most 40 characters" in reply
          and "a_fact_name_that_is_far_too_long_to_be_kept: a fact name is lowercase words" in reply
          and "premises_county: a skill counts deadlines from it; load that skill first" in reply)
    check("item 112: propose_facts refuses words the tenant never typed, a how other than stated or inferred, a text over 300 characters",
          "rent_amount: said must be" in reply and "objected: how must be" in reply
          and "long_story: value must be at most 300 characters" in reply)
    check("item 112: propose_facts refuses a value equal to the confirmed one", "claim_notice_received: already confirmed" in reply)
    check("propose_facts never confirms", "vacated" not in record.matter["facts"])
    # "said" shortened with "...": each piece must be the tenant's words. "already confirmed" means the words passed.
    joined = propose_facts.invoke({"facts_json": json.dumps({"claim_notice_received": {
        "value": False, "how": "stated", "said": "Actually I moved out on July 29... I never got any letter..."}})})
    check("propose_facts takes the tenant's words joined by an ellipsis (gpt-oss run, m-023)", "already confirmed" in joined)
    invented = propose_facts.invoke({"facts_json": json.dumps({"claim_notice_received": {
        "value": False, "how": "stated", "said": "Actually I moved out ... I got a letter"}})})
    check("propose_facts refuses an ellipsis joining words the tenant never typed", "said must be" in invented)
    check("propose_facts refuses JSON that is not an object", "must be a JSON object" in propose_facts.invoke({"facts_json": "[1]"})
          and "not valid JSON" in propose_facts.invoke({"facts_json": "{"}))

    # the confirmation: only the proposals, and a changed fact with both values
    rows = pending_rows()
    changed = next(r for r in rows if r["id"] == "claim_notice_received")
    check("item 112: the confirmation lists only the proposals, in the order proposed, each with a label, a type, the "
          "suggestion, and the tenant's words; no fact the record lacks is a row",
          [r["id"] for r in rows] == ["tenancy_terminated", "claim_notice_received", "claim_notice_date", "claim_notice_dated",
                                      "claim_delivery", "claim_reason", "vacated", "landlord_response", "move_in_date"]
          and {r["id"]: r["type"] for r in rows} == {
              "tenancy_terminated": "date", "claim_notice_received": "text", "claim_notice_date": "date",
              "claim_notice_dated": "date", "claim_delivery": "text", "claim_reason": "text", "vacated": "date",
              "landlord_response": "text", "move_in_date": "text"}
          and rows[0]["label"] == "tenancy terminated" and rows[0]["suggested"] == "2026-07-31"
          and rows[0]["basis"] == "My lease ended July 31, 2026")
    check("item 112: a proposal for a fact already confirmed with another value is a changed row, showing both",
          changed["status"] == "changed" and changed["confirmed"] is False and changed["suggested"] is True
          and row_notes(changed)[0] == "was no, now yes?" and {r["status"] for r in rows if r is not changed} == {"proposed"})
    facts_part = prompt_part("facts")
    check("item 112: YOUR FACTS gives the confirmed facts, the proposals waiting, and what the deadlines still need with "
          "the id, the type, and what each counts for",
          facts_part.startswith("Confirmed by the tenant:\n- claim_notice_received: no\n- deposit_amount: 1850\n\n")
          and "Proposed, waiting for the tenant to confirm after your reply (what they told you, not confirmed):\n"
              "- tenancy_terminated: 2026-07-31\n- claim_notice_received: yes\n" in facts_part and "\n- vacated: 2026-07-29\n" in facts_part
          and "- tenancy_terminated (date): counted from by the landlord's 15-day deadline of Fla. Stat. 83.49(3)(a); counted "
              "from by the landlord's 30-day deadline of Fla. Stat. 83.49(3)(a) [deposit not returned]\n" in facts_part
          and "- early_or_periodic (bool): decides whether the 83.49(5) deadline counts [deposit not returned]" in facts_part
          and "- claim_notice_date (date): counted from by the tenant's 15-day deadline of Fla. Stat. 83.49(3)(b) "
              "[deposit claim received]" in facts_part)

    # accept, correct, bad input asked again, a changed fact, a skip
    prompt_before_sheet = system_prompt()
    shown_sheet = io.StringIO()
    with contextlib.redirect_stdout(shown_sheet):
        saved = run_sheet(scripted(["", "", "", "", "", "cleaning and carpet", "maybe", "7/28/2026", "?", ""]))
    facts = record.matter["facts"]
    check("item 112: the confirmation saves every answered fact", len(saved) == 8)
    check("sheet: Enter accepts a suggestion", facts["tenancy_terminated"] == "2026-07-31")
    check("sheet: a typed answer replaces a suggestion, and a bad one is asked again",
          facts["vacated"] == "2026-07-28" and "Please type a date like 2026-07-31 or 7/31/2026" in shown_sheet.getvalue()
          and facts["claim_reason"] == "cleaning and carpet")
    check("sheet: a changed fact takes the new value, shown beside the old with the tenant's words",
          facts["claim_notice_received"] == "yes" and "was no, now yes?" in shown_sheet.getvalue()
          and 'suggested: yes, from your words: "I got a letter from the landlord"' in shown_sheet.getvalue())
    check("item 112: the confirmation asks no question of a skill and shows no lease clause",
          "What date" not in shown_sheet.getvalue() and "your lease" not in shown_sheet.getvalue()
          and "tenancy terminated (YYYY-MM-DD)" in shown_sheet.getvalue())
    check("item 112: a skipped fact stays pending, and the tenant is told it is asked again",
          [r["id"] for r in pending_rows()] == ["landlord_response"] and "landlord_response" in record.matter["proposed"]
          and "Skipped for now: landlord response." in shown_sheet.getvalue() and "asked again" in shown_sheet.getvalue())
    after_sheet = json.loads(deadline_listing())
    got = {d["clock"]: str(d.get("deadline")) for d in after_sheet["deadlines"]}
    check("item 112: a deadline computes from the confirmed clock dates, and waiting lists what is not confirmed",
          got == {"return_if_no_claim": "2026-08-15", "claim_notice_deadline": "2026-08-30",
                  "tenant_objection_deadline": "2026-10-10", "landlord_remit_balance": "2026-10-22"}
          and after_sheet["waiting"] == {"deposit_not_returned": ["early_or_periodic"]})
    append_transcript({"role": "tenant", "text": "I left before the lease was up."})
    propose_facts.invoke({"facts_json": json.dumps({"early_or_periodic": {
        "value": True, "how": "inferred", "said": "I left before the lease was up"}})})
    with contextlib.redirect_stdout(io.StringIO()):
        run_sheet(scripted(["", ""]))                          # the skipped fact is asked again, then the new one
    deadlines = {d["clock"]: str(d.get("deadline")) for d in json.loads(deadline_listing())["deadlines"]}
    check("sheet: a skipped fact is asked again at the next confirmation; a yes confirms a clock's applies_if fact",
          facts["landlord_response"] == "said he would send a check next week" and facts["early_or_periodic"] is True
          and not pending_rows())
    check("get_deadlines answers once every clock fact is confirmed",
          deadlines.get("tenant_objection_deadline") == "2026-10-10" and deadlines.get("tenant_seven_day_notice") == "2026-07-21"
          and "waiting" not in json.loads(deadline_listing()))
    listed = json.loads(deadline_listing())["deadlines"]
    shared = [d for d in listed if d["clock"] == "claim_notice_deadline"]
    events_now = len(read_events())
    status_text = prompt_part("deadlines")
    check("item 46: the prompt shows each computed deadline as passed or upcoming, with no date, and logs nothing",
          "- claim notice deadline [deposit not returned, deposit claim received]: the landlord's, 30 days after "
          "tenancy terminated, Fla. Stat. 83.49(3)(a): passed" in status_text
          and not re.search(r"\b[a-z]+(?:_[a-z]+)+\b", status_text)
          and not re.search(r"\b20\d\d-\d\d-\d\d\b", status_text) and len(read_events()) == events_now)
    loaded_part = prompt_part("loaded")
    check("item 53: a loaded skill reaches the model under its name with its open questions and no clock id, and the "
          "rules forbid writing the prompt's part names",
          loaded_part.startswith("# deposit_not_returned\n## When to load this skill") and "\n# deposit_claim_received\n" in loaded_part
          and "## What the statute does not settle" in loaded_part and "termination_date_meaning" not in loaded_part
          and "no part name in capitals as this prompt writes it" in system_prompt())
    old_names = re.compile(r"LEASE PROFILE|PLAYBOOKS|STATUTE SECTIONS|CASE TOPICS|ELEMENT STATUS|DEADLINE STATUS|"
                           r"THE TOOL'S NOTES ON YOUR ISSUES|WHAT THE STATUTE DOES NOT SETTLE \(")
    prompt_now = system_prompt([HumanMessage(content="Can you write a letter to my landlord?")])     # rule 6 in too
    heads = [prompt_now.index("\n\n" + name + ":\n") for name in PARTS.values()]
    check("item 61: the prompt's parts go under names a tenant can read, in order, with no old part name left in "
          "the prompt, the rules, or a tool's description",
          heads == sorted(heads) and not old_names.search(prompt_now + CASE_RULE + NO_CASES_RULE + LETTER_RULE)
          and not any(old_names.search(t.description) for t in model_tools)
          and "## Letters" in prompt_part("loaded") and "open_questions" not in prompt_part("loaded"))
    check("item 52: the fallback line is ruled out where an open question or a case topic is on the point",
          "the fallback line only when no stored sentence, no open question in a loaded skill's \"What the statute does not "
          "settle\", and no topic in COURT CASES THIS TOOL HAS" in system_prompt())
    check("item 56: rule 1's So gives each reading of an open question, never one as the answer, and rule 5 sends the "
          "model to a loaded skill's open questions",
          "what follows on each of its readings, never one of them as the answer" in system_prompt()
          and "5. The open questions in a loaded skill's \"What the statute does not settle\" stay open, with their readings."
          in system_prompt())
    check("item 73: rule 1 asks for every rule the answer turns on with its cite, and the format line to cite, not recite",
          "Instead: each rule the answer turns on, each condition and each consequence you rely on, with the cite" in system_prompt()
          and "Cite, do not recite:" in system_prompt())
    check("item 46: the rules apply the law, and a loaded skill's open questions reach the model with their readings",
          "1. Apply the law to the tenant's facts." in system_prompt() and "stay open, with their readings" in system_prompt()
          and "give every reading" in prompt_part("loaded"))
    check("item 112: rule 4 has the model propose what the tenant tells it, the tenant confirm after the reply, and ask in the "
          "chat only for what the answer turns on; no rule says a sheet asks every missing fact",
          "4. You propose facts; the tenant confirms them after your reply." in system_prompt()
          and "Ask in the chat only for what your answer turns on" in system_prompt()
          and "the sheet asks" not in system_prompt() and "the sheet confirms" not in system_prompt())
    check("a deadline two skills share is listed once, with both skills", len(shared) == 1
          and shared[0]["skills"] == ["deposit_not_returned", "deposit_claim_received"])
    printed = render_deadlines(deadline_listing())
    receipt = get_deadlines.invoke({"type": "tool_call", "id": "d0", "name": "get_deadlines", "args": {}})
    check("item 44: get_deadlines prints the listing and gives the model a receipt with no date in it",
          json.loads(receipt.artifact)["deadlines"] == listed and not re.search(r"\b20\d\d-\d\d-\d\d\b", receipt.content)
          and "printed the tenant's deadlines" in receipt.content and "call get_deadlines again" in receipt.content)
    call = AIMessage(content="", tool_calls=[{"name": "get_deadlines", "args": {}, "id": "d0"}])
    shown_now = turn_blocks([call, receipt], [call, receipt])
    check("the chat loop prints the listing, dates included, not the model's receipt",
          [b["kind"] for b in shown_now] == ["deadlines"]
          and all(d["deadline"] in screen(shown_now) for d in listed if "deadline" in d)
          and "You are not shown the dates" not in screen(shown_now))
    check("printed deadlines carry every field: date, actor, rule, start, cite, status, counting, skills",
          all(f"  {d['deadline']}  {d['actor']} deadline: " in printed for d in listed)
          and printed.count("counting: ") == len(listed) and "Fla. Stat. 83.49(3)(b)" in printed
          and "[deposit_not_returned, deposit_claim_received], passed" in printed and "tenancy terminated 2026-07-31" in printed)
    timeline_now = render_timeline()
    check("the timeline shows a shared deadline once, tagged with both skills",
          timeline_now.count("claim notice deadline") == 1
          and "[deposit_not_returned, deposit_claim_received] landlord deadline: claim notice deadline" in timeline_now)
    check("timeline <skill> keeps a shared deadline under either skill",
          "claim notice deadline" in render_timeline("deposit_claim_received")
          and "claim notice deadline" in render_timeline("deposit_not_returned"))
    check("item 112: the timeline's confirmed dates are the facts whose value is a date, a plain-text fact among them, each by its id in "
          "words; a date only one loaded skill counts from is left out of another skill's timeline",
          re.search(r"2025-08-01\s+move in date\b", timeline_now) and re.search(r"2026-07-28\s+vacated\b", timeline_now)
          and "claim notice received" not in timeline_now and "deposit amount" not in timeline_now
          and "move in date" in render_timeline("deposit_claim_received") and "vacated" not in render_timeline("deposit_claim_received")
          and "claim notice date" not in render_timeline("deposit_not_returned"))
    facts_after = prompt_part("facts")
    check("item 112: YOUR FACTS follows the record: the confirmed facts with their values, no proposal waiting, nothing the "
          "deadlines still need",
          "\n- vacated: 2026-07-28\n" in facts_after and "\n- early_or_periodic: yes\n" in facts_after
          and "\n\nProposed, waiting for the tenant to confirm after your reply (what they told you, not confirmed):\nnone\n" in facts_after
          and facts_after.endswith("nothing: every fact the loaded skills' deadlines count from is confirmed"))
    check("the prompt changes when the record does", prompt_before_sheet != system_prompt())

    # a reply's cites: a fetched section counts as shown; a failed cite is printed, transcribed, and logged
    fetch_call = AIMessage(content="", tool_calls=[{"name": "get_statute_section", "args": {"section": "83.505"}, "id": "c1"}])
    check("a section the model fetched counts as shown", "83.505" in sections_shown([fetch_call]))
    cautions = "\n".join(check_reply(f'See Fla. Stat. 83.49(3)(a) and 83.64. Under 83.49(3)(b): "{FORFEIT}"', []))
    flagged = [e for e in read_events()[events_before:] if e["kind"] in ("cite_flagged", "quote_flagged")]
    check("a flagged cite and quote are printed and logged, a good cite is not",
          "[Check: 83.64" in cautions and "[Check: 83.49" not in cautions
          and [(e["kind"], e.get("cite")) for e in flagged] == [("cite_flagged", "83.64"), ("quote_flagged", "83.49(3)(b)")])
    events_now = len(read_events())
    retold_text = (f'Fla. Stat. 83.49(3)(a): "{FORFEIT}"\nUnder 83.49(3)(b), if you do not object within 15 days, they '
                   f'may deduct (Lease Section 4.3).')
    retold = check_reply(retold_text, [])
    cited = cited_words(retold_text)
    lease_43 = next(c for _, c in record.profile.clauses() if c.present and c.section and c.section.startswith("4.3"))
    check("item 73: a section cited without a quote gets no caution and no event (item 66's caution is gone); the "
          "program prints the words of each cite, the narrowest once, and the lease clause with its page",
          retold == [] and len(read_events()) == events_now
          and cited.startswith(CITED_HEAD) and "\n\nFla. Stat. 83.49(3)(a): (a) Upon the vacating" in cited
          and "\n\nFla. Stat. 83.49(3)(b): (b) Unless the tenant objects" in cited and "Fla. Stat. 83.49:" not in cited
          and f"Lease Section 4.3, page {lease_43.page} (what the landlord may keep from the deposit" in cited
          and [b["kind"] for b in turn_blocks([AIMessage(content=retold_text)], [])] == ["reply", "sources", "footer"]
          and cited_words("You said nothing about the law.") == "")
    page_cited = cited_words("The landlord is the one named in your lease (Lease, page 1).")
    check("item 77: a page cite prints the clauses on that page with no section number, each with its label",
          "Lease, page 1 (the landlord's name and address): " in page_cited and "Lease, page 1 (the tenants' names): " in page_cited
          and "Section" not in page_cited)
    # cases (wiki.py, get_cases): nothing is offered until a page is verified; a verified, tagged page offers its
    # topics, prints by code, and is logged; an untagged page never shows; a case cite must be one shown
    check("no case topic is offered while no page is verified, and the prompt says so",
          offered_topics() == {} and prompt_part("cases") == "none for these issues")
    # rules that can apply only sometimes (prompt.rules_for): letters once a letter is in play, cases in full
    # only with a topic to offer
    check("the letter rule is in when a letter is in play: a letter drafted (this matter has one), or asked for",
          any(ev["kind"] == "draft" for ev in read_events()) and LETTER_RULE in system_prompt()
          and LETTER_RULE in system_prompt([HumanMessage(content="Can you write a letter to my landlord?")]))
    check("with no case topic, rule 8 is one line saying there are none",
          NO_CASES_RULE in system_prompt() and CASE_RULE not in system_prompt())
    verified_copy = Path(tempfile.mkdtemp()) / "wiki"
    shutil.copytree(WIKI, verified_copy)
    verify("Durene v. Alcime", "Smoke", verified_copy)
    verify("Hankins v. Smith", "Smoke", verified_copy)          # untagged: for research only
    wiki.ROOT = verified_copy
    try:
        offered = offered_topics()
        check("a verified, tagged page offers its topics for the active sections; an untagged one does not",
              offered.get("Landlord's notice of claim on the deposit") == 1 and "Constructive eviction" not in offered)
        check("with a case topic offered, rule 8 is the full rule", CASE_RULE in system_prompt())
        topic = "Landlord's notice of claim on the deposit"
        call = AIMessage(content="", tool_calls=[{"name": "get_cases", "args": {"topic": topic}, "id": "k1"}])
        shown_msg = get_cases.invoke({"type": "tool_call", "id": "k1", "name": "get_cases", "args": {"topic": topic}})
        out = screen(turn_blocks([call, shown_msg], [call, shown_msg]))   # get_cases ends the turn: no reply follows
        check("get_cases prints every verified case on the topic in the courts' words with the closing line, and logs it",
              "Durene v. Alcime, 448 So. 2d 1208 (Fla. 3d DCA 1984)" in out and "readily available fund" in out
              and "\nCasey v. Picinich, " not in out and "How far one reaches your situation turns on how alike its facts are" in out
              and read_events()[-1]["kind"] == "cases_shown" and read_events()[-1]["cases"] == ["448 So. 2d 1208"])
        check("item 47: the tenant and the model get the same cases, with their facts and how other cases treat them",
              shown_msg.artifact in shown_msg.content and "readily available fund" in shown_msg.content
              and "Petitioner vacated the subject residential property" in out and "Distinguished by Plakhov v. Serova" in out
              and "[[" not in out)
        again = get_cases.invoke({"type": "tool_call", "id": "k2", "name": "get_cases", "args": {"topic": topic}})
        check("the same topic asked again in the session prints one line pointing up and logs nothing",
              again.artifact == f'The cases on "{topic}" are printed above in this chat.'
              and "already printed above" in again.content and read_events()[-1]["kind"] == "cases_shown"
              and sum(e["kind"] == "cases_shown" for e in read_events()) == 1)
        refused = get_cases.invoke({"type": "tool_call", "id": "k3", "name": "get_cases", "args": {"topic": "Constructive eviction"}})
        check("get_cases refuses a topic that is not offered, and the tenant sees the topics there are",
              refused.content.startswith("No case topic") and topic in refused.artifact
              and refused.artifact.startswith('This tool has no case topic named "Constructive eviction"'))
        check("a topic written with its case count or in other letter case is the topic (eval, 2026-10-01)",
              topic_named("Landlord's notice of claim on the deposit (1)", offered) == topic
              and topic_named("landlord’s notice of claim on the deposit", offered) == topic
              and topic_named("Notice of claim", offered) is None)
        check("a case cite in a reply must be one the tool showed in the chat",
              check_case_cites("See 448 So. 2d 1208 and 573 So. 2d 76.", shown_msg.content) == [("573 So. 2d 76", "is not a case this tool showed in this chat")])
        # item 57: two cases printed; a reply that names one and gives the other's words as its own is cautioned
        verify("Malagon v. Solari", "Smoke", verified_copy)
        printed_two = wiki.render_cases(topic)
        call_two = AIMessage(content="", tool_calls=[{"name": "get_cases", "args": {"topic": topic}, "id": "k4"}])
        shown_two = ToolMessage(content="The program printed these cases:\n\n" + printed_two, artifact=printed_two,
                                name="get_cases", tool_call_id="k4")
        parts = dict(printed_cases([shown_two]))
        malagon_words = re.findall(r'"([^"]{30,90})', parts["Malagon v. Solari"])[0]
        wrong = AIMessage(content=f'In Durene v. Alcime, 448 So. 2d 1208, the court wrote: "{malagon_words}"')
        events_now = len(read_events())
        wrong_screen = screen(turn_blocks([call_two, shown_two, wrong], [call_two, shown_two, wrong]))
        right = AIMessage(content=f'In Durene v. Alcime the court held a notice must be timely. In Malagon v. Solari: "{malagon_words}"')
        right_screen = screen(turn_blocks([call_two, shown_two, right], [call_two, shown_two, right]))
        check("item 57: a printed case no reply names gets a caution and an event; a quote credited to the wrong "
              "printed case is flagged; a reply naming each case, quoting each right, gets neither",
              list(parts) == ["Durene v. Alcime", "Malagon v. Solari"]
              and "this reply does not discuss: Malagon v. Solari." in wrong_screen
              and "is in Malagon v. Solari's text, not Durene v. Alcime's" in wrong_screen
              and [e["kind"] for e in read_events()[events_now:]] == ["quote_flagged", "cases_left_out"]
              and "does not discuss" not in right_screen and "[Check:" not in right_screen
              and "a reply left out printed cases: Malagon v. Solari" in render_timeline(full=True))
    finally:
        wiki.ROOT = WIKI
        shutil.rmtree(verified_copy.parent)
    said = " ".join(record.matter["description"].split()[:8])          # the first words of the description
    check("the tenant's description counts as what the model was given", len(said) >= 20
          and check_quoted(f'You said "{said}"', given_text([])) == [] and check_quoted(f'"{said}"', "") != [])

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
    check("every fact is confirmed on the sheet", len(confirmations) == 10
          and all(e["confirmed_in"] == "sheet" for e in confirmations))
    lines = [json.loads(line) for line in (matter_dir() / "sessions" / f"{sid}.jsonl").read_text().splitlines()]
    check("the transcript holds the tenant's words and every sheet answer",
          [line["role"] for line in lines].count("tenant") == 2 and [line["role"] for line in lines].count("sheet") == 10)
    check("the transcript holds every caution: a cite and a quote, then item 57's wrong case and case left out",
          [line["text"][:17] for line in lines if line["role"] == "check"]
          == ["[Check: 83.64 was", "[Check: the quote", "[Check: the quote", "[Check: the progr"])

    # the timeline
    full, plain = render_timeline(full=True), render_timeline()
    check("timeline full shows the session with its transcript", f"session {sid[:8]} started" in full
          and f"sessions/{sid}.jsonl" in full)
    check("the plain timeline leaves sessions out", "session" not in plain)
    check("the timeline shows a tenant update", "tenant update: The landlord emailed me again" in plain)
    check("the plain timeline marks a corrected date", "tenant (corrected, confirmed" in plain)
    check("timeline full marks a corrected fact with the suggestion it replaced",
          "claim reason = cleaning and carpet" in full and "corrected from stated cleaning" in full)
    check("timeline full keeps the tag of an accepted suggestion",
          "fact confirmed: claim delivery = certified mail" in full and "corrected from stated certified" not in full)
    check("the timeline keeps same-day events in log order",
          full.index(f"session {sid[:8]} started") < full.index(f"session {sid[:8]} ended"))
finally:
    remove_scratch("t-smoke")
check("the scratch matter is removed", not (MATTERS / "t-smoke").exists())

# a county is words (item 112): a clock fact of type "county", proposed once the skill is loaded and confirmed as text
make_scratch("t-smoke-county", skills=["notice_received_nonpayment"], facts={}, proposed={})
try:
    load_matter("t-smoke-county", "m-001")
    start_session("existing")
    append_transcript({"role": "tenant", "text": "The notice was taped to my door on November 24, 2026. I live in Alachua County."})
    reply = propose_facts.invoke({"facts_json": json.dumps({
        "nonpayment_notice_delivered": {"value": "2026-11-24", "how": "stated",
                                        "said": "taped to my door on November 24, 2026"},
        "premises_county": {"value": "Alachua", "how": "stated", "said": "I live in Alachua County"}})})
    empty = propose_facts.invoke({"facts_json": json.dumps({
        "premises_county": {"value": "", "how": "stated", "said": "I live in Alachua County"}})})
    rows = pending_rows()
    check("item 112: a county is a clock fact typed county, taken as non-empty text (an empty one is refused), and its row is "
          "asked as words",
          "Proposed: nonpayment_notice_delivered, premises_county." in reply and "premises_county: value must be some words" in empty
          and record.clock_facts()["premises_county"] == "county"
          and [(r["id"], r["type"]) for r in rows] == [("nonpayment_notice_delivered", "date"), ("premises_county", "county")])
    shown_sheet = io.StringIO()
    with contextlib.redirect_stdout(shown_sheet):
        run_sheet(scripted(["", ""]))
    listing = json.loads(deadline_listing())
    check("item 112: a court-days clock is dated once its date and county are confirmed; the date the notice states is waited for",
          "premises county (county name)" in shown_sheet.getvalue() and record.matter["facts"]["premises_county"] == "Alachua"
          and [(d["clock"], str(d["deadline"])) for d in listing["deadlines"]] == [("three_day_demand_period", "2026-12-01")]
          and listing["waiting"] == {"notice_received_nonpayment": ["notice_stated_payment_date"]})
    # letters read every confirmed fact value (item 112): a plain-text fact's amount and date are in the record
    record.matter["facts"].update(rent_paid="1,278", paid_on="2026-10-03", note_to_landlord="I paid $50 extra")
    check("item 112: a letter's dates and amounts are checked against every confirmed fact value, whatever its type",
          not_in_record("I paid $1,278 on October 3 and $50 more.", date.today()) == []
          and not_in_record("I paid $1,279.", date.today()) == ["$1,279"])
    end_session()
finally:
    remove_scratch("t-smoke-county")
check("the county scratch matter is removed", not (MATTERS / "t-smoke-county").exists())
print()
