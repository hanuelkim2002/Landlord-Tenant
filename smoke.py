"""Smoke Tests, offline: each block checks one piece without the agent and without a model call, so it runs
with no key. Needs the saved test matter, matters/t-test/test-001/. The model calls are in smoke_online.py.
The last section runs the code that writes to a matter on a throwaway copy and prints named checks: every
line must be OK, like the playbook quote checks.

    python smoke.py
"""
import contextlib
import io
import json
import logging
import re
import shutil
import tempfile
from datetime import date, timedelta
from pathlib import Path

import PyPDF2
from langchain.agents import create_agent
from langchain.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langgraph.checkpoint.memory import InMemorySaver
from streamlit.testing.v1 import AppTest

import record
from calendars import court_calendars
from checks import TEST_MATTER, check, make_scratch, remove_scratch, summary
from citations import (SUBSECTION_START, check_case_cites, check_cites, check_quoted, cites_without_quote,
                       quoted_passages, subsections)
from config import CASES, MATTERS, WIKI
from corpus import check_all_playbooks, load_playbook, playbooks, statute
from deterministic import NOT_JSON, ask_json, check_elements, check_options, compute_deadlines, lease_value
from dev.build_cases import court_text
import wiki
from wiki import lint, read_pages, verified, verify
from record import (append_event, append_transcript, end_session, list_matters, load_matter, matter_dir,
                    new_matter_id, read_events, start_session)
from lease import FOOTER, lease_clauses
from sheet import STOP_LINE, pending_rows, run_sheet, stop_text
from timeline import render_deadlines, render_timeline
from agent import (CASE_RULE, CITED_HEAD, LETTER_RULE, NO_CASES_RULE, PARTS, READING_LINE, check_reply, cited_words, command, given_text, print_blocks,
                   printed_cases, retry_empty, sections_shown, sheet_note, system_prompt, thread_config, turn,
                   turn_blocks)
from tools import build_letter, deadline_listing, draft_letter, get_cases, get_deadlines, get_statute_section, offered_topics, propose_facts, topic_named
from tools import tools as model_tools

load_matter("t-test", "test-001")         # the test matter and its lease profile, from disk
pb = playbooks["deposit_not_returned"]

# listing and loading: every saved matter, then what load_matter put in record
print(list_matters())
print(record.matter["tenant"], record.matter["id"], record.matter["issues"], type(record.profile).__name__)
print()

# playbook checks: quotes (spec and prose) against the statute text, shape, and shared facts
check("every playbook check is OK", check_all_playbooks() == 0)
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
print(deadline_listing())
record.matter["proposed"] = {}
print()

# court business days (83.56(3)): the circuit's holiday calendar, the count, and refusing instead of guessing
nonpayment = playbooks["notice_received_nonpayment"]
def three_day(delivered, county):
    row = next(d for d in compute_deadlines(nonpayment, {"nonpayment_notice_delivered": delivered, "premises_county": county},
                                            today=date(2026, 9, 27)) if d["clock"] == "three_day_demand_period")
    return str(row.get("deadline")), row
check("court calendar: every holiday date is in its memorandum", all(
    re.sub(r"\s+", "", h["as_printed"].removeprefix("Note: ")) in re.sub(r"\s+", "", "\n".join(
        p.extract_text() for p in PyPDF2.PdfReader(entry["document"]).pages))
    for cal in court_calendars for entry in cal["years"].values() for h in entry["holidays"]))
check("court days skip Thanksgiving, the Friday after, and the weekend", three_day("2026-11-24", "Alachua")[0] == "2026-12-01")
check("court days cross into the next year's memorandum", three_day("2026-12-30", "Alachua County")[0] == "2027-01-06")
check("court days refuse a year with no memorandum loaded", three_day("2027-12-29", "Alachua")[1]["status"].startswith("not computed"))
check("court days refuse a county with no calendar", three_day("2026-11-24", "Miami-Dade")[1]["status"].startswith("not computed"))
check("a court-day date carries its counting line", "Eighth Judicial Circuit" in three_day("2026-11-24", "Alachua")[1]["counting"])
refused = {**three_day("2026-11-24", "Miami-Dade")[1], "issues": ["notice_received_nonpayment"]}
check("a refused court-day count is printed with its reason and no date", render_deadlines(json.dumps(
      {"deadlines": [refused]})).splitlines()[1].startswith("  (no date)   three day demand period [notice_received_nonpayment]: not computed"))
stated = {"nonpayment_notice_delivered": "2026-09-18", "premises_county": "Alachua", "notice_stated_payment_date": "2026-09-21"}
row = next(d for d in compute_deadlines(nonpayment, stated, today=date(2026, 9, 27)) if d["clock"] == "three_day_demand_period")
check("the notice's stated date is printed beside the 83.56(3) date once confirmed, not before (item 10)",
      "beside it, from your record: notice stated payment date 2026-09-21" in render_deadlines(json.dumps(
      {"deadlines": [{**row, "issues": ["notice_received_nonpayment"]}]}, default=str))
      and "shown_with" not in three_day("2026-09-18", "Alachua")[1])
with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as bad:
    bad.write(Path("playbooks/notice_received_nonpayment.yaml").read_text().replace(
        "shown_with: notice_stated_payment_date", "shown_with: amount_demanded"))
try:
    load_playbook(bad.name)
    refused = False
except ValueError as e:
    refused = "is not a date element" in str(e)
check("a shown_with that is not a date element is refused when the playbook loads", refused)
check("no deadline at all is said in one line, not an empty heading (an issue with no clocks)",
      render_deadlines(json.dumps({"deadlines": []})) == "No deadlines: none of the deadlines this tool computes "
      "applies to your confirmed facts." and "waiting [rent_increased]" in render_deadlines(
      json.dumps({"deadlines": [], "waiting": {"rent_increased": ["new_rent"]}})))
print()

# cases/ (dev/build_cases.py): the court's text only. Every file is named for the cite on its first line and
# carries none of Westlaw's material; the build drops headnote markers but keeps the court's own brackets.
WESTLAW_MARKS = ("West Headnotes", "Synopsis", "KeyCite", "Thomson Reuters", "Negative Treatment",
                 "End of Document", "cite this headnote", "More cases on this issue", "Procedural Posture")
case_texts = {f.name: f.read_text() for f in sorted(CASES.glob("*.txt"))}
check("cases/ holds opinions", len(case_texts) > 0)
check("every case file is named for the cite on its first line", all(
    name == re.sub(r"[^A-Za-z0-9 ]", "", text.split("\n")[0].removesuffix(" (Mem)")).replace(" ", "_") + ".txt"
    for name, text in case_texts.items()))
check("no case file carries Westlaw's material (headnotes, synopsis, KeyCite, copyright, negative treatment)",
      not any(mark in text for text in case_texts.values() for mark in WESTLAW_MARKS))
check("no headnote marker opens a line in a case file", not any(
    re.match(r"\s*\[\d+\]", line) for text in case_texts.values() for line in text.split("\n")))
check("every case file has its attorneys and its parallel cites", all(
    "Attorneys and Law Firms" in text and "All Citations" in text for text in case_texts.values()))
built = court_text(["448 So.2d 1208", "District Court of Appeal of Florida,", "Synopsis", "Tenant sued.",
                    "West Headnotes (2)", "[1]", "Attorneys and Law Firms", "*1209 Counsel, for petitioner.",
                    "Opinion", "[1] [2] We agree. See 13 Fla. Law Weekly [1116] 1117.", "All Citations", "448 So.2d 1208"])
check("the build keeps the caption and the court's text, drops the synopsis and headnotes, and keeps a bracket "
      "beyond the headnote count", built.startswith("448 So.2d 1208\nDistrict Court of Appeal of Florida,\n"
      "Attorneys and Law Firms") and "\nWe agree. See 13 Fla. Law Weekly [1116] 1117.\n" in built
      and "Tenant sued." not in built and "West Headnotes" not in built)
print()

# the case wiki (wiki.py): the real pages pass every check, and on a throwaway copy each kind of fault is caught
check("every wiki check is OK (python wiki.py check)", not lint()[0])
wiki_copy = Path(tempfile.mkdtemp()) / "wiki"
shutil.copytree(WIKI, wiki_copy)
def wiki_fault(page, old, new):
    """lint's problems with one change made to one page of the copy; the page is put back after."""
    path = next(wiki_copy.glob(f"*/{page}.md"))
    text = path.read_text()
    path.write_text(text.replace(old, new, 1))
    found = lint(wiki_copy)[0]
    path.write_text(text)
    return " | ".join(found)
check("a wiki quote with a word changed is caught",
      "is not in 448 So. 2d 1208" in wiki_fault("Durene v. Alcime", "readily available fund", "readily usable fund"))
check("a wiki quote's wrong pin page is caught, also for a quote that runs across a page break",
      "starts at 1210, not 1209" in wiki_fault("Durene v. Alcime", 'fund of money." (at 1210)', 'fund of money." (at 1209)')
      and "starts at 1222, not 1223" in wiki_fault("Plakhov v. Serova", 'pretrial stipulation." (at 1222)',
                                                   'pretrial stipulation." (at 1223)'))
check("a wiki quote with no source is caught",
      "a quote with no source" in wiki_fault("Casey v. Picinich", "Reasoning: none stated.",
                                             'Reasoning: "the court gave no reasons for this at all".'))
check("a statute quote cited to the wrong subsection is caught", "is in 83.49(3)(c), not 83.49(3)(b)" in wiki_fault(
      "Fees and costs in a suit over the deposit", "(Fla. Stat. 83.49(3)(c))", "(Fla. Stat. 83.49(3)(b))"))
check("a wiki link to no page is caught",
      "goes to no page" in wiki_fault("Casey v. Picinich", "[[Durene v. Alcime]] (1984)", "[[Durene v Alcime]] (1984)"))
check("a case page with no section tag must say why (scope_note)",
      "no section tag and no scope_note" in wiki_fault("Casey v. Picinich", 'sections: ["83.49"]', "sections: []")
      and "no section tag" not in wiki_fault("Casey v. Picinich", 'sections: ["83.49"]',
                                             'sections: []\nscope_note: Reads part I only.'))
check("a case missing from the Cases list of a topic it names is caught", "whose Cases list does not have it" in
      wiki_fault("Constructive eviction", "- [[Plakhov v. Serova]], Fla. 4th DCA", "- Plakhov v. Serova, Fla. 4th DCA"))
verify("Casey v. Picinich", "Smoke", wiki_copy)
signed = verified(read_pages(wiki_copy)["Casey v. Picinich"])
casey = wiki_copy / "cases" / "Casey v. Picinich.md"
casey.write_text(casey.read_text().replace("pro se", "pro se, without a lawyer", 1))
check("a verified wiki page counts as verified until it is edited, and the edit is a warning",
      signed and not verified(read_pages(wiki_copy)["Casey v. Picinich"])
      and any("changed since Smoke verified it" in w for w in lint(wiki_copy)[1]))
durene = wiki_copy / "cases" / "Durene v. Alcime.md"
durene.write_text(durene.read_text().replace("readily available fund", "readily usable fund"))
try:
    verify("Durene v. Alcime", "Smoke", wiki_copy)
    refused = False
except ValueError:
    refused = True
check("verify refuses a wiki page that has a problem", refused)
shutil.rmtree(wiki_copy.parent)
print()

# a tenant fact next to the lease field its playbook names (compare_to): shown only when they differ
def row_for(fact_id, facts, proposed={}):
    return next(r for r in check_elements(pb, record.profile, facts, proposed) if r["id"] == fact_id)
check("a tenant date that differs from the lease carries the lease's words",
      row_for("tenancy_terminated", {"tenancy_terminated": "2026-07-31"}).get("lease_says") == record.profile.term_end.quote)
check("a tenant date that matches the lease carries nothing",
      "lease_says" not in row_for("tenancy_terminated", {"tenancy_terminated": lease_value("date", record.profile.term_end.quote)}))
check("a suggestion is compared with the lease too", "lease_says" in row_for(
      "tenancy_terminated", {}, {"tenancy_terminated": {"value": "2026-07-31", "how": "stated", "basis": "x"}}))
check("lease amounts are read from the printed figure", lease_value("money", record.profile.security_deposit.quote) == 1850)
print()

# the letter template
record.matter["issues"] = ["deposit_not_returned"]
record.matter["facts"] = dict(test_facts)
print(build_letter("Return the $1,850.00 deposit to 12 Elm St, Gainesville FL 32601", 10, "certified mail, return receipt requested",
                   [{"cite": "Fla. Stat. 83.49(3)(a)", "text": pb.spec.clocks[0].quote}]))
print()

check("a letter's request ends with one period, whatever the ask ends with",
      "32601.\n" in build_letter("Return the deposit to 12 Elm St, Gainesville FL 32601.", 10, "certified mail", [])
      and ".." not in build_letter("Return the deposit to 12 Elm St, Gainesville FL 32601.", 10, "certified mail", []))
print()

# cites in a reply (citations.py): subsections are found in every stored section, and each kind of bad cite is
# caught. A cite to a real, shown subsection passes even when it is the wrong one for the point (items 6, 11).
def markers_in_order(section):
    """Numbers run 1, 2, 3 and, after each number, letters run a, b, c."""
    seq = [m.group(1) for m in SUBSECTION_START.finditer(statute[section])]
    numbers = [int(x) for x in seq if x.isdigit()]
    letters_ok, previous = True, None
    for x in seq:
        if x.isdigit():
            previous = None
            continue
        letters_ok = letters_ok and x == ("a" if previous is None else chr(ord(previous) + 1))
        previous = x
    return numbers == list(range(1, len(numbers) + 1)) and letters_ok


check("every stored section's subsection markers run in order", all(markers_in_order(s) for s in statute))
start, end = subsections("83.49")["(3)(b)"]
check("83.49(3)(b) is the objection paragraph", statute["83.49"][start:end].startswith("(b) Unless the tenant objects"))
start, end = subsections("83.56")["(5)(a)"]
check("a lettered subsection right after its number is found (83.56(5)(a))", statute["83.56"][start:end].startswith("(a) If the landlord"))
check("a cite to a shown section and a real subsection passes", check_cites("See Fla. Stat. 83.49(3)(a).", {"83.49"}) == [])
check("a cite written with a space is read the same", check_cites("s. 83.51 (1)", {"83.51"}) == [])
check("a section not shown or fetched is flagged", check_cites("Under 83.64 the landlord", {"83.49"})[0][0] == "83.64")
check("a subsection the section lacks is flagged", "does not have" in check_cites("83.49(3)(f)", {"83.49"})[0][1])
check("a section not in the corpus is flagged", "is not a section" in check_cites("83.99", {"83.49"})[0][1])
check("the same cite twice is flagged once", len(check_cites("83.64 and again 83.64", set())) == 1)
check("a cite inside a quoted passage is the quote's own, not the reply's (live run 2026-09-30)", check_cites(
      '"by certified mail to the tenant’s last known mailing address or by e-mail in accordance with s. 83.505 of his '
      'or her intention" (Fla. Stat. 83.49(3)(a))', {"83.49"}) == [])
check("a short quoted cite is still checked", check_cites('"cite": "83.64"', {"83.49"})[0][0] == "83.64")
check("item 11's wrong claim passes this check (its cite is real and shown)",
      check_cites("you may terminate the lease under Fla. Stat. 83.56(1)", set(playbooks["repair_not_made"].sections)) == [])

# a model answer that is not valid JSON at intake is asked for again (deterministic.ask_json; 3 of 51 intakes
# crashed on one in the eval of 2026-10-01): a stand-in model answers badly once, then well
class Answers:
    def __init__(self, *texts):
        self.texts, self.prompts = list(texts), []
    def invoke(self, prompt):
        self.prompts.append(prompt)
        return AIMessage(content=self.texts.pop(0))
flaky = Answers('{"issues": ["other"] "reason": "x"}', '```json\n{"issues": ["other"], "reason": "x"}\n```')
check("ask_json asks again after an answer that is not JSON, saying so",
      ask_json(flaky, "Classify.") == {"issues": ["other"], "reason": "x"} and len(flaky.prompts) == 2
      and flaky.prompts[1].endswith(NOT_JSON))
broken = Answers("no", "still no", "never")
try:
    ask_json(broken, "Classify.")
    gave_up = False
except json.JSONDecodeError:
    gave_up = len(broken.prompts) == 3
check("ask_json gives up after three answers that are not JSON", gave_up)
two_lines = Answers('{"issues": ["other"], "reason": "he said he regrets\nrenting to people like you"}')
check("ask_json keeps a line break inside a quoted string (the mixed story's crash, eval 2026-10-01)",
      ask_json(two_lines, "Classify.")["reason"] == "he said he regrets\nrenting to people like you"
      and len(two_lines.prompts) == 1)

# quotes in a reply (citations.check_quoted): which cite goes with which quote, then what each is checked against
FORFEIT = "he or she forfeits the right to impose a claim upon the security deposit"     # in 83.49(3)(a)
OBJECTS = "Unless the tenant objects to the imposition of the landlord’s claim"          # in 83.49(3)(b)
check("a cite in a heading before a quote goes with it",
      quoted_passages(f'**Statute quote (Fla. Stat. 83.49(3)(b)):**\n"{OBJECTS}"') == [(OBJECTS, "83.49(3)(b)")])
check("a cite after a quote goes with it, and not with the next quote",
      [c for q, c in quoted_passages(f'- "{FORFEIT}" (83.49(3)(a))\n- Lease: "Tenant shall notify Landlord in writing"')]
      == ["83.49(3)(a)", ""])
check("a cite inside a repeated tool result goes with no quote",
      quoted_passages('"cite": "83.56(3)",\n    "counting": "court business days, start day not counted"')[0][1] == "")
check("a quote in its cited subsection passes, whatever its apostrophes",
      check_quoted(f'"{OBJECTS.replace("’", chr(39))}" (83.49(3)(b))', "") == [])
check("a quote with an ellipsis passes when each piece is in the subsection",
      check_quoted('"If the landlord fails to give the required written notice ... he or she forfeits the right" (83.49(3)(a))', "") == [])
check("item 6: a real sentence cited to the wrong subsection is flagged with the right one",
      check_quoted(f'"{FORFEIT}" (83.49(3)(b))', "")[0][2] == "is in 83.49(3)(a), not 83.49(3)(b)")
check("item 5: words the statute does not have, inside quote marks, are flagged",
      check_quoted('"Unless the tenant objects in writing within 15 days" (83.49(3)(b))', "")[0][2] == "is not in 83.49")
check("a quote cited to the wrong section names the section that has it",
      check_quoted(f'"{FORFEIT}" (83.56)', "")[0][2] == "is not in 83.56; it is in 83.49")
check("a quote with no cite passes when it is in what the model was given",
      check_quoted('You wrote "I will not pay rent until it is fixed."', "saying I will not pay rent until it is fixed") == [])
check("a quote with no cite is flagged when it is nowhere",
      "not word for word" in check_quoted('You asked for "repair within 5 days".', "Give them 5 days to reply.")[0][2])
check("item 14: an id in quote marks is not a quote (m-023)",
      check_quoted('"claim_notice_deadline" (83.49(3)(a))', "") == [])
check("item 14: an example after e.g. is not a quote (m-022)",
      check_quoted('what to fix (e.g., "repair the air-conditioning unit")', "") == [])
check("item 14: the same words without e.g. are still checked",
      check_quoted('You asked: "repair the air-conditioning unit"', "") != [])
check("a short quote keeps its two marks, so the words after it are not read as a quote (eval, 2026-10-01)",
      quoted_passages(f'If you choose "assert," the letter will quote: Fla. Stat. 83.49(3)(a): "{FORFEIT}"')
      == [(FORFEIT, "83.49(3)(a)")]
      and check_quoted(f'If you choose "assert," the letter will quote: Fla. Stat. 83.49(3)(a): "{FORFEIT}"', "") == [])
check("a quote that runs over two lines is one passage",
      [q for q, c in quoted_passages('Lease Section 4.3: "Tenant shall notify Landlord in writing\nof a forwarding address" and "x"')]
      == ["Tenant shall notify Landlord in writing\nof a forwarding address"])
check("item 58: a quote holding the statute's own quoted words passes with its inner marks changed to single ones",
      check_quoted("Fla. Stat. 83.53(2): “The landlord may enter the dwelling unit upon reasonable notice to the tenant "
                   "and at a reasonable time for the purpose of repair of the premises. ‘Reasonable notice’ for the "
                   "purpose of repair is notice given at least 24 hours prior to the entry”", "") == [])
check("item 58: the tool's own words pass though the prompt holds them as YAML, with an apostrophe doubled",
      check_quoted('The tool says: "It is not: the disturbance is the neighbor\'s failure of 83.52(7)"',
                   "- 'It is not: the disturbance is the neighbor''s failure of 83.52(7)'") == [])
check("item 54: a cite retold with none of its words quoted is found; one whose words are quoted, or whose "
      "subsection holds the quote, is not",
      cites_without_quote(f'Fla. Stat. 83.49(3)(a): "{FORFEIT}". Under 83.49(3) that is so. Under Fla. Stat. '
                          f'83.49(3)(b), if you do not object within 15 days, they may deduct.') == ["83.49(3)(b)"]
      and cites_without_quote(f'Fla. Stat. 83.49(3)(a): "{FORFEIT}"') == [])
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


def screen(blocks):
    """The blocks' texts as one string, to look for what the tenant would read."""
    return "\n".join(b["text"] for b in blocks)


def prompt_part(key):
    """One part of the system prompt as it stands now (agent.PARTS), without its name."""
    after = system_prompt().split("\n\n" + PARTS[key] + ":\n")[1]
    later = list(PARTS.values())[list(PARTS).index(key) + 1:]
    return after.split("\n\n" + later[0] + ":\n")[0] if later else after


make_scratch("t-smoke",
             issues=["deposit_not_returned", "deposit_claim_received"],
             facts={"claim_notice_received": False},
             proposed={"tenancy_terminated": stated("2026-07-31", "My lease ended July 31, 2026"),
                       "claim_notice_received": stated(True, "I got a letter from the landlord"),
                       "claim_notice_date": stated("2026-09-25", "on September 25, 2026"),
                       "claim_notice_dated": stated("2026-09-22", "dated September 22, 2026"),
                       "claim_delivery": stated("certified mail", "by certified mail"),
                       "claim_amount": stated(400, "keeping $400"),
                       "claim_reason": stated("cleaning", "for cleaning"),
                       "deposit_amount": stated(1850, "my $1,850 deposit"),          # the lease gives it: stale
                       "seven_day_notice_given": stated(False, "no notice")})        # waits on early_or_periodic
try:
    load_matter("t-smoke", "m-001")
    check("list_matters finds the scratch matter", {"tenant": "t-smoke", "id": "m-001"}.items()
          <= next((m for m in list_matters() if m["tenant"] == "t-smoke"), {}).items())
    check("new_matter_id counts the tenant's matters", new_matter_id("t-smoke") == "m-002")
    events_before = len(read_events())

    sid = start_session("existing")
    check("start_session opens a session", record.session == sid)
    record.prune_proposals()
    check("prune drops a suggestion the lease already answers", "deposit_amount" not in record.matter["proposed"])
    check("prune keeps a suggestion whose condition is still open", "seven_day_notice_given" in record.matter["proposed"])
    check("prune keeps a suggestion whose condition has a change pending", "claim_notice_date" in record.matter["proposed"])

    # propose_facts: one suggestion taken, five refused, each for its own reason
    append_transcript({"role": "tenant", "text": "Actually I moved out on July 29, 2026. I never got any letter."})
    said = "I moved out on July 29, 2026"
    reply = propose_facts.invoke({"facts_json": json.dumps({
        "vacated": {"value": "2026-07-29", "how": "stated", "said": said},
        "rent_amount": {"value": 1200, "how": "stated", "said": said},
        "forwarding_address_given": {"value": True, "how": "stated", "said": "I told them by phone"},
        "early_or_periodic": {"value": "not sure", "how": "stated", "said": said},
        "objected": {"value": False, "how": "guessed", "said": said},
        "claim_notice_received": {"value": False, "how": "stated", "said": "I never got any letter"},
    })})
    check("propose_facts takes a well-formed suggestion", "Suggested: vacated." in reply)
    check("propose_facts refuses a fact the issues do not ask for", "rent_amount: not a fact" in reply)
    check("propose_facts refuses words the tenant never typed", "forwarding_address_given: said must be" in reply)
    check("propose_facts refuses a value of the wrong type", "early_or_periodic: value must be yes or no" in reply)
    check("propose_facts refuses a how other than stated or inferred", "objected: how must be" in reply)
    check("propose_facts refuses a value already confirmed", "claim_notice_received: already confirmed" in reply)
    check("propose_facts never confirms", "vacated" not in record.matter["facts"])
    # "said" shortened with "...": each piece must be the tenant's words. "already confirmed" means the words passed.
    joined = propose_facts.invoke({"facts_json": json.dumps({"claim_notice_received": {
        "value": False, "how": "stated", "said": "Actually I moved out on July 29... I never got any letter..."}})})
    check("propose_facts takes the tenant's words joined by an ellipsis (gpt-oss run, m-023)", "already confirmed" in joined)
    invented = propose_facts.invoke({"facts_json": json.dumps({"claim_notice_received": {
        "value": False, "how": "stated", "said": "Actually I moved out ... I got a letter"}})})
    check("propose_facts refuses an ellipsis joining words the tenant never typed", "said must be" in invented)
    check("get_deadlines waits while facts are open", deadline_listing().startswith("Not yet"))
    check("item 46: while facts are open, the prompt's deadline status says what each issue waits for",
          "- waiting [deposit not returned]: no deadline until these are confirmed: " in prompt_part("deadlines"))
    check("printed deadlines say none yet, and what is waiting",
          render_deadlines(deadline_listing()).startswith("No deadlines yet")
          and "waiting [deposit_not_returned]: " in render_deadlines(deadline_listing()))

    # the intake sheet: accept, correct, bad input asked again, a changed fact, an applies_if fact, a skip
    prompt_before_sheet = system_prompt()
    shown_sheet = io.StringIO()
    with contextlib.redirect_stdout(shown_sheet):
        saved = run_sheet(scripted(["", "7/28/2026", "maybe", "", "", "y", "no", "", "", "$1,2x", "400",
                                    "cleaning and carpet", "?", "no"]))
    facts = record.matter["facts"]
    check("sheet saves every answered fact", len(saved) == 11)
    check("sheet: Enter accepts a suggestion", facts["tenancy_terminated"] == "2026-07-31")
    check("sheet: a typed answer replaces a suggestion", facts["vacated"] == "2026-07-28")
    check("sheet: a changed fact takes the new value", facts["claim_notice_received"] is True)
    check("sheet: an applies_if fact is asked once it applies", facts.get("claim_notice_date") == "2026-09-25")
    check("sheet: a bad amount is asked again, then saved", facts["claim_amount"] == 400)
    check("sheet: yes/no answers are saved as true/false", facts["forwarding_address_given"] is True
          and facts["early_or_periodic"] is False)
    check("sheet: the lease's words appear where they differ",
          f'your lease says: "{record.profile.term_end.quote}"' in shown_sheet.getvalue())
    check("sheet: a fact two issues share is asked once", shown_sheet.getvalue().count("What date did the lease end") == 1
          and shown_sheet.getvalue().count("receive the landlord's written notice") == 1)
    check("prune drops a suggestion once its condition is confirmed no",
          "seven_day_notice_given" not in record.matter["proposed"])
    check("sheet: a skipped fact stays open", [r["id"] for r in pending_rows()] == ["notice_states_objection_window"])
    with contextlib.redirect_stdout(io.StringIO()):
        run_sheet(scripted(["yes"]))
    deadlines = {d["clock"]: str(d.get("deadline")) for d in json.loads(deadline_listing())["deadlines"]}
    check("get_deadlines answers once every fact is confirmed", deadlines.get("tenant_objection_deadline") == "2026-10-10")
    listed = json.loads(deadline_listing())["deadlines"]
    shared = [d for d in listed if d["clock"] == "claim_notice_deadline"]
    events_now = len(read_events())
    status_text = prompt_part("deadlines")
    check("item 46: the prompt shows each computed deadline as passed or upcoming, with no date, and logs nothing",
          "- claim notice deadline [deposit not returned, deposit claim received]: the landlord's, 30 days after "
          "tenancy terminated, Fla. Stat. 83.49(3)(a): passed" in status_text
          and not re.search(r"\b[a-z]+(?:_[a-z]+)+\b", status_text)
          and not re.search(r"\b20\d\d-\d\d-\d\d\b", status_text) and len(read_events()) == events_now)
    open_part = prompt_part("open")
    check("item 53: the open questions reach the model without their ids, and the rules forbid writing the prompt's part names",
          "readings:" in open_part and "termination_date_meaning" not in open_part
          and "no part name in capitals as this prompt writes it" in system_prompt())
    old_names = re.compile(r"LEASE PROFILE|PLAYBOOKS|STATUTE SECTIONS|CASE TOPICS|ELEMENT STATUS|DEADLINE STATUS")
    prompt_now = system_prompt([HumanMessage(content="Can you write a letter to my landlord?")])     # rule 6 in too
    heads = [prompt_now.index("\n\n" + name + ":\n") for name in PARTS.values()]
    check("item 61: the prompt's parts go under names a tenant can read, in order, with no old part name left in "
          "the prompt, the rules, or a tool's description",
          heads == sorted(heads) and not old_names.search(prompt_now + CASE_RULE + NO_CASES_RULE + LETTER_RULE)
          and not any(old_names.search(t.description) for t in model_tools)
          and "postures:" in prompt_part("notes") and "open_questions" not in prompt_part("notes"))
    check("item 52: the fallback line is ruled out where an open question or a case topic is on the point",
          "the fallback line only when no stored sentence, no open question in WHAT THE STATUTE DOES NOT SETTLE, and no "
          "topic in COURT CASES THIS TOOL HAS" in system_prompt())
    check("item 56: the open questions' part says the stored text settles none, and rule 1's So gives each reading",
          "settles none of them, so give every reading and pick none):\n" in system_prompt()
          and "what follows on each of its readings, never one of them as the answer" in system_prompt())
    check("item 73: rule 1 asks for every rule the answer turns on with its cite, and the format line to cite, not recite",
          "Instead: each rule the answer turns on, each condition and each consequence you rely on, with the cite" in system_prompt()
          and "Cite, do not recite:" in system_prompt())
    check("item 46: the rules apply the law, and open questions reach the model with their readings",
          "1. Apply the law to the tenant's facts." in system_prompt() and "stay open, with their readings" in system_prompt()
          and "readings:" in prompt_part("open"))
    check("a deadline two issues share is listed once, with both issues", len(shared) == 1
          and shared[0]["issues"] == ["deposit_not_returned", "deposit_claim_received"])
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
    check("printed deadlines carry every field: date, actor, rule, start, cite, status, counting, issues",
          all(f"  {d['deadline']}  {d['actor']} deadline: " in printed for d in listed)
          and printed.count("counting: ") == len(listed) and "Fla. Stat. 83.49(3)(b)" in printed
          and "[deposit_not_returned, deposit_claim_received], passed" in printed and "tenancy terminated 2026-07-31" in printed)
    timeline_now = render_timeline()
    check("the timeline shows a shared deadline once, tagged with both issues",
          timeline_now.count("claim notice deadline") == 1
          and "[deposit_not_returned, deposit_claim_received] landlord deadline: claim notice deadline" in timeline_now)
    check("timeline <issue> keeps a shared deadline under either issue",
          "claim notice deadline" in render_timeline("deposit_claim_received")
          and "claim notice deadline" in render_timeline("deposit_not_returned"))
    status_now = json.loads(prompt_part("facts"))
    check("the prompt's element status is the record as it is now", any(
          r["id"] == "vacated" and r["status"] == "known" and r["value"] == "2026-07-28"
          for r in status_now["deposit_not_returned"]))
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
    lease_43 = next(c for _, c in record.profile if c.present and c.section and c.section.startswith("4.3"))
    check("item 73: a section cited without a quote gets no caution and no event (item 66's caution is gone); the "
          "program prints the words of each cite, the narrowest once, and the lease clause with its page",
          retold == [] and len(read_events()) == events_now
          and cited.startswith(CITED_HEAD) and "\n\nFla. Stat. 83.49(3)(a): (a) Upon the vacating" in cited
          and "\n\nFla. Stat. 83.49(3)(b): (b) Unless the tenant objects" in cited and "Fla. Stat. 83.49:" not in cited
          and f"Lease Section {lease_43.section}, page {lease_43.page}: " in cited
          and [b["kind"] for b in turn_blocks([AIMessage(content=retold_text)], [])] == ["reply", "sources", "footer"]
          and cited_words("You said nothing about the law.") == "")
    # cases (wiki.py, get_cases): nothing is offered until a page is verified; a verified, tagged page offers its
    # topics, prints by code, and is logged; an untagged page never shows; a case cite must be one shown
    check("no case topic is offered while no page is verified, and the prompt says so",
          offered_topics() == {} and prompt_part("cases") == "none for these issues")
    # rules that can apply only sometimes (agent.rules_for): letters once a letter is in play, cases in full
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
    check("every fact is confirmed on the sheet", len(confirmations) == 12
          and all(e["confirmed_in"] == "sheet" for e in confirmations))
    lines = [json.loads(line) for line in (matter_dir() / "sessions" / f"{sid}.jsonl").read_text().splitlines()]
    check("the transcript holds the tenant's words and every sheet answer",
          [line["role"] for line in lines].count("tenant") == 1 and [line["role"] for line in lines].count("sheet") == 12)
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
print()


# ---- Issues as suggestions, on a second scratch copy with one issue. Confirming "received a notice: yes" on
# the sheet suggests deposit_claim_received; the tenant says yes to it and its questions and guidance follow.
# Then: a rejected issue is not suggested again by its rule unless the fact is confirmed anew, a classifier
# suggestion asks again, and an active issue can be dropped. Nothing leaves the history.
make_scratch("t-smoke-related", issues=["deposit_not_returned"], facts={"claim_notice_received": False},
             proposed={"claim_notice_received": stated(True, "I got a letter from the landlord")})
try:
    load_matter("t-smoke-related", "m-001")
    sid = start_session("existing")
    check("a related issue is not suggested before its fact is confirmed", record.add_related_issues() == []
          and record.matter["issues"] == ["deposit_not_returned"] and record.matter["proposed_issues"] == [])
    shown_sheet = io.StringIO()
    def accept_notice_and_issue(prompt):
        """Answer by the question on screen: accept the change to "received a notice", say yes to the suggested
        issue, skip the rest."""
        last_question = [line for line in shown_sheet.getvalue().splitlines() if line.startswith("  ") and
                         not line.startswith("    ")][-1]
        if "received any written notice" in last_question:
            return ""
        return "yes" if "Is that part of your situation?" in last_question else "?"
    with contextlib.redirect_stdout(shown_sheet):
        run_sheet(accept_notice_and_issue)
    events = read_events()
    proposed = [e for e in events if e["kind"] == "issue_proposed"]
    check("confirming the fact suggests the related issue, with its source and reason", proposed
          and proposed[-1]["issue"] == "deposit_claim_received" and proposed[-1]["source"] == "related"
          and proposed[-1]["because"] == "claim_notice_received is true" and proposed[-1]["session"] == sid)
    check("the sheet asks about the suggested issue before its facts, and yes makes it active",
          "Suggested for your matter: deposit_claim_received" in shown_sheet.getvalue()
          and "This looks like: Tenant has received the landlord's written notice" in shown_sheet.getvalue()
          and shown_sheet.getvalue().index("Is that part of your situation?") < shown_sheet.getvalue().index("What date is printed on the landlord's notice?")
          and record.matter["issues"] == ["deposit_not_returned", "deposit_claim_received"]
          and any(e["kind"] == "issue_confirmed" and e["issue"] == "deposit_claim_received" for e in events))
    check("the model's next prompt has the new issue's guidance", "issue: deposit_claim_received" in system_prompt())
    check("the prompt carries the sections the active playbooks name", "=== 83.49 ===" in system_prompt())
    sections_before = prompt_part("statute")
    record.add_issues(["other"], "classify", "a smoke check")        # "other" is the one label with no playbook
    check("an issue with no playbook is recorded at once and adds no sections", "other" in record.matter["issues"]
          and prompt_part("statute") == sections_before)
    check("add_issues never adds an issue twice", record.add_issues(["deposit_claim_received"], "classify", "x") == [])
    check("timeline full shows the suggestion and the confirmation", "issue suggested: deposit claim received"
          in render_timeline(full=True) and "issue confirmed: deposit claim received" in render_timeline(full=True))
    # deadlines per issue: deposit_not_returned complete, deposit_claim_received still open (its facts skipped)
    record.matter["facts"].update(tenancy_terminated="2026-07-31", vacated="2026-07-30", claim_notice_date="2026-09-25",
                                  forwarding_address_given=True, early_or_periodic=False)
    per_issue = json.loads(deadline_listing())
    check("an issue with open facts does not block another issue's deadlines",
          {d["clock"] for d in per_issue["deadlines"]} == {"return_if_no_claim", "claim_notice_deadline"}
          and all(d["issues"] == ["deposit_not_returned"] for d in per_issue["deadlines"])
          and "deposit_claim_received" in per_issue["waiting"] and "deposit_not_returned" not in per_issue["waiting"])
    check("printed deadlines show one issue's dates and the other issue waiting",
          "return if no claim" in render_deadlines(json.dumps(per_issue, default=str))
          and "waiting [deposit_claim_received]: " in render_deadlines(json.dumps(per_issue, default=str)))
    # dropping, rejecting, and asking again
    record.matter["proposed"]["claim_amount"] = stated(400, "keeping $400")
    record.reject_issue("deposit_claim_received", "issue_dropped")
    check("drop takes an issue out, logs it, and clears its pending suggestions",
          "deposit_claim_received" not in record.matter["issues"] and "claim_amount" not in record.matter["proposed"]
          and read_events()[-1]["kind"] == "issue_dropped")
    check("the rule does not suggest a dropped issue again on its own", record.add_related_issues() == [])
    record.confirm_fact("claim_notice_received", False, "sheet")
    record.confirm_fact("claim_notice_received", True, "sheet")        # the notice fact confirmed anew
    check("the rule suggests it again when its fact is confirmed anew",
          [p["issue"] for p in record.matter["proposed_issues"]] == ["deposit_claim_received"])
    record.reject_issue("deposit_claim_received")
    check("no on the sheet rejects a suggestion and logs it", record.matter["proposed_issues"] == []
          and read_events()[-1]["kind"] == "issue_rejected" and "deposit_claim_received" in record.matter["rejected_issues"])
    record.add_issues(["deposit_claim_received"], "classify", "the tenant's update")
    check("a later classification suggests a rejected issue again",
          [p["issue"] for p in record.matter["proposed_issues"]] == ["deposit_claim_received"]
          and "deposit_claim_received" not in record.matter["rejected_issues"])

    # an empty reply (m-018): the model is asked once more; a stand-in agent plays the model's second turn
    class Again:
        def __init__(self, reply):
            self.reply = reply
        def invoke(self, inputs, config):
            return {"messages": first["messages"] + inputs["messages"] + [AIMessage(content=self.reply)]}
    first = {"messages": [HumanMessage(content="What are my deadlines?"), AIMessage(content="\n")]}
    shown_first = turn_blocks(first["messages"][1:], first["messages"])
    _, _, shown_again = retry_empty(Again("The deadlines appear above."), {}, first)
    check("a turn with only blank text shows nothing, and the model's second reply is shown", shown_first == []
          and shown_again == [{"kind": "reply", "text": "The deadlines appear above."}]
          and read_events()[-1]["kind"] == "reply_empty" and read_events()[-1]["recovered"] is True)
    _, _, shown_again = retry_empty(Again(""), {}, first)
    check("a second empty reply tells the tenant and is logged, with why each answer stopped",
          [b["kind"] for b in shown_again] == ["caution"] and "[Check: no reply came back" in screen(shown_again)
          and read_events()[-1]["recovered"] is False
          and read_events()[-1]["finish"] == [None, None])

    # the tool's own line under a reply that quotes the statute without it (TODO item 30): printed by the program
    # and kept in the transcript; not under a reply that has it, nor under one quoting only the tenant
    bare = AIMessage(content=f'Fla. Stat. 83.49(3)(a): "{FORFEIT}"')
    shown_bare = turn_blocks([bare], [bare])
    shown_others = (turn_blocks([AIMessage(content=f'Fla. Stat. 83.49(3)(a): "{FORFEIT}"\n{READING_LINE}')], [])
                    + turn_blocks([AIMessage(content='You said: "I paid the whole rent for September myself."')], []))
    session_lines = (record.matter_dir() / "sessions" / f"{record.session}.jsonl").read_text().splitlines()
    footers = [json.loads(line) for line in session_lines if json.loads(line)["role"] == "footer"]
    check("item 46: a reply that quotes the statute gets the program's reading line, once, in the transcript; "
          "none under one that already has it or quotes only the tenant",
          shown_bare[-1] == {"kind": "footer", "text": READING_LINE} and screen(shown_others).count(READING_LINE) == 1
          and [f["text"] for f in footers] == [READING_LINE])
    lease_words = next(c.quote for _, c in record.profile if c.present and c.quote and len(c.quote) > 60)[:60]
    cut = AIMessage(content="You confirmed you moved out on", response_metadata={"finish_reason": "length"})
    check("item 47: a reply stopped at the length limit gets a caution saying it was cut off",
          [b["kind"] for b in turn_blocks([cut], [cut])] == ["reply", "caution"]
          and "cut off at the model's length limit" in screen(turn_blocks([cut], [cut])))
    check("a lease quote gets the program's reading line too (eval, 2026-10-01)",
          screen(turn_blocks([AIMessage(content=f'Lease Section 4.3, page 2: "{lease_words}"')], [])).count(READING_LINE) == 1)

    # blocks (TODO item 31): what the tenant sees from a turn or a command, the model's words apart from the
    # program's, for the terminal and the web page alike
    bad_cite = AIMessage(content=f'Fla. Stat. 83.49(3)(a): "{FORFEIT}"\nSee also 83.64.')
    check("a reply's blocks: the model's words, the words it cites, then the program's cautions, then its line",
          [b["kind"] for b in turn_blocks([bad_cite], [bad_cite])] == ["reply", "sources", "caution", "footer"])
    with contextlib.redirect_stdout(io.StringIO()) as printed:
        print_blocks([{"kind": "reply", "text": "One."}, {"kind": "footer", "text": "Two."}])
    check("the terminal prints each block's text with an empty line after it", printed.getvalue() == "One.\n\nTwo.\n\n")
    commands_before = [json.loads(line)["role"] for line in
                       (record.matter_dir() / "sessions" / f"{record.session}.jsonl").read_text().splitlines()].count("command")
    issues_shown, timeline_shown = command("issues"), command("timeline full")
    check("chat commands come back as the program's blocks, and words that are not one go to the model",
          [b["kind"] for b in issues_shown] == ["notice"] and "deposit_not_returned: " in screen(issues_shown)
          and [b["kind"] for b in timeline_shown] == ["timeline"] and "DATE" in screen(timeline_shown)
          and command("timeline nonsense")[0]["text"].startswith("No issue named nonsense")
          and command("What issues do I have?") is None and command("drop") is None)
    check("each command goes to the transcript", [json.loads(line)["role"] for line in
          (record.matter_dir() / "sessions" / f"{record.session}.jsonl").read_text().splitlines()].count("command")
          == commands_before + 3)
    check("what the tenant confirmed on a sheet goes to the model with the next message",
          sheet_note([("vacated", "2026-07-28"), ("issue deposit_claim_received", "confirmed")])
          == "[Program note: the tenant confirmed on the sheet: vacated = 2026-07-28, issue deposit_claim_received = confirmed]\n"
          and sheet_note([]) == "")
    # one whole turn through an agent: a stand-in model proposes a fact, then replies; the turn's blocks are the
    # reply only, it says facts were proposed, and a second turn starts after the first one's messages
    class Proposes(GenericFakeChatModel):
        def bind_tools(self, tools, **kwargs):
            return self
    said = "I got a letter from the landlord"
    proposes = Proposes(messages=iter([
        AIMessage(content="", tool_calls=[{"name": "propose_facts", "id": "p1", "args": {"facts_json": json.dumps(
            {"claim_notice_received": {"value": True, "how": "stated", "said": said}})}}]),
        AIMessage(content=f'You said: "{said}"'), AIMessage(content="Second turn.")]))
    agent_now = create_agent(proposes, tools=model_tools, checkpointer=InMemorySaver())
    config_now = thread_config()
    first_blocks, first_proposed = turn(agent_now, config_now, said)
    second_blocks, second_proposed = turn(agent_now, config_now, "And?", note="[Program note: x]\n")
    check("turn: the reply is shown, the proposal noted, and the next turn shows only its own reply",
          first_blocks == [{"kind": "reply", "text": f'You said: "{said}"'}] and first_proposed
          and second_blocks == [{"kind": "reply", "text": "Second turn."}] and not second_proposed
          and config_now["configurable"]["thread_id"] == record.session)

    # get_deadlines and get_cases no longer end the model's turn (items 47 and 51; get_deadlines did from item 19):
    # a stand-in model calls get_deadlines, then applies the status; the reply comes after the printed listing
    class StandIn(GenericFakeChatModel):
        def bind_tools(self, tools, **kwargs):
            return self
    applies = "The program's listing above shows the 7-day period has not passed yet."
    stand_in = StandIn(messages=iter([AIMessage(content="", tool_calls=[{"name": "get_deadlines", "args": {}, "id": "d1"}]),
                                      AIMessage(content=applies)]))
    ended = create_agent(stand_in, tools=model_tools).invoke(
        {"messages": [HumanMessage(content="If I get rid of the dog by Friday, am I safe?")]})
    check("item 51: neither get_deadlines nor get_cases ends the turn; the model's answer follows the printed listing",
          not get_deadlines.return_direct and not get_cases.return_direct
          and [m.type for m in ended["messages"][-2:]] == ["tool", "ai"] and ended["messages"][-1].content == applies
          and "your instructions say which have passed" in ended["messages"][-2].content)

    # item 65: a question about when, answered without get_deadlines: the program prints the deadlines above the
    # reply; when the model calls it, the listing is printed once, not twice
    events_now = len(read_events())
    skips = StandIn(messages=iter([AIMessage(content="It is seven days before you move out."),
                                   AIMessage(content="", tool_calls=[{"name": "get_deadlines", "args": {}, "id": "d2"}]),
                                   AIMessage(content="The listing is above.")]))
    agent_when = create_agent(skips, tools=model_tools, checkpointer=InMemorySaver())
    when_blocks, _ = turn(agent_when, thread_config(), "When do I have to tell them?")
    asked_blocks, _ = turn(agent_when, thread_config(), "When is the last day?")
    session_lines = [json.loads(line) for line in
                     (matter_dir() / "sessions" / f"{record.session}.jsonl").read_text().splitlines()]
    check("item 65: asked when, a turn without get_deadlines gets the deadlines printed by the program first, logged "
          "and transcribed; a turn that calls it gets one listing",
          [b["kind"] for b in when_blocks] == ["deadlines", "reply"]
          and when_blocks[0]["text"] == render_deadlines(deadline_listing())
          and [b["kind"] for b in asked_blocks] == ["deadlines", "reply"]
          and any(e["kind"] == "deadlines_computed" for e in read_events()[events_now:])
          and sum(line.get("what") == "deadlines" for line in session_lines) == 1)

    # the same letter twice in one session (m-026): drafted once; a changed letter is drafted again
    letter_args = {"issue": "deposit_not_returned", "posture": "preserve", "ask": "Return the deposit",
                   "respond_within_days": 10, "delivery_method": "certified mail"}
    draft_letter.invoke(letter_args)
    again = draft_letter.invoke(letter_args)
    changed = draft_letter.invoke({**letter_args, "respond_within_days": 14})
    drafts = [e for e in read_events() if e["kind"] == "draft" and e.get("session") == record.session]
    check("the same letter twice in a session is drafted once", again.startswith("[The same letter was already drafted")
          and len(drafts) == 2 and "Please respond by" in changed)
    dropped = command("drop deposit_not_returned")                 # the last covered issue: the chat ends
    check("drop as a command takes the issue out, logs it, and says the chat ends when no covered issue is left",
          [b["text"] for b in dropped] == ["Dropped deposit_not_returned from this matter. It is logged, and it can be "
                                           "suggested again later.", "No issue this tool covers is left in this matter, "
                                           "so the chat ends here."]
          and read_events()[-1]["kind"] == "issue_dropped" and not record.active_playbooks())
    end_session()
finally:
    remove_scratch("t-smoke-related")
check("the second scratch matter is removed", not (MATTERS / "t-smoke-related").exists())
print()


# ---- Every playbook through the real code path, on a scratch matter: the sheet asks every question (a "yes"
# to every yes/no, so every applies_if question comes up), every clock gets a date, and a letter carries the
# playbook's note to the tenant. A new playbook is covered without a new check.
def answer_by_type(shown_so_far):
    """An ask function that answers the question on screen by its type hint."""
    def ask(prompt):
        last = [line for line in shown_so_far.getvalue().splitlines() if line.startswith("  ") and
                not line.startswith("    ")][-1]
        if "What county" in last:
            return "Alachua"                             # a county with a stored court holiday calendar
        for hint, answer in (("(YYYY-MM-DD)", "2026-10-31"), ("(yes/no)", "yes"), ("(amount)", "1200"), ("(words)", "a test answer")):
            if last.endswith(hint):
                return answer
        return "?"
    return ask

# the letter rule on a matter with no letter drafted (the test matter's history has one, so it is emptied)
make_scratch("t-smoke-rules")
try:
    (MATTERS / "t-smoke-rules" / "m-001" / "events.jsonl").write_text("")
    load_matter("t-smoke-rules", "m-001")
    check("the letter rule is left out while no letter is in play",
          LETTER_RULE not in system_prompt([HumanMessage(content="What are my deadlines?")])
          and LETTER_RULE in system_prompt([HumanMessage(content="Can you help me write something to send them?")]))
finally:
    remove_scratch("t-smoke-rules")

# options before steps (TODO item 72, deterministic.check_options): the author's AC story of 2026-10-04 leaves
# ending the lease not settled; a roof leak with every step taken is open; caused by the tenant, closed; a gate's
# fact not confirmed, not known yet. The prompt gives the statuses in words.
repair = playbooks["repair_not_made"]
today = date.today()
ac = {"problem_is_structure_or_plumbing": False, "caused_by_tenant_side": False, "rent_paid_since_known": True,
      "written_notice_delivered": True, "written_notice_date": str(today - timedelta(days=30)),
      "notice_states_termination_intent": False, "notice_states_withholding_intent": False}
roof = {**ac, "problem_is_structure_or_plumbing": True, "rent_paid_since_known": False,
        "notice_states_termination_intent": True, "written_notice_date": str(today - timedelta(days=10))}
by_id = lambda facts: {o["option"]: o for o in check_options(repair, facts, today)}
ac_options, roof_options = by_id(ac), by_id(roof)
roof_soon = by_id({**roof, "written_notice_date": str(today - timedelta(days=2))})
check("item 72: an AC not repaired leaves ending the lease and withholding rent not settled, each gate and step in its state",
      ac_options["end_the_lease"]["status"] == "not settled" and ac_options["withhold_rent"]["status"] == "not settled"
      and [g["status"] for g in ac_options["end_the_lease"]["gates"]] == ["not settled", "met", "not settled"]
      and [s["status"] for s in ac_options["end_the_lease"]["steps"]] == ["done", "to do", "to do"]
      and "turns on a building" in ac_options["end_the_lease"]["gates"][0]["why"])
check("item 72: a roof leak with the notice given and the 7 days passed is open; with the 7 days still running, open and waiting",
      roof_options["end_the_lease"]["status"] == "open"
      and [s["status"] for s in roof_options["end_the_lease"]["steps"]] == ["done", "done", "done"]
      and [s["status"] for s in roof_soon["end_the_lease"]["steps"]] == ["done", "done", "waiting"]
      and roof_options["end_the_lease"]["also_open"] == ["material_noncompliance"])
check("item 72: caused on the tenant's side closes both options; a gate's fact not confirmed leaves them not known yet",
      {o["status"] for o in by_id({**roof, "caused_by_tenant_side": True}).values()} == {"closed"}
      and by_id({k: v for k, v in roof.items() if k != "problem_is_structure_or_plumbing"})["end_the_lease"]["status"] == "not known yet")
make_scratch("t-smoke-options", issues=["repair_not_made"], facts=ac, proposed={})
try:
    load_matter("t-smoke-options", "m-001")
    options_part = system_prompt().split("\n\n" + PARTS["options"] + ":\n")[1].split("\n\n")[0]
    check("item 72: the prompt gives each option's status, conditions, and steps in words, with no id, and rule 1 asks for it first",
          "End the lease because the landlord has not made the repair (Fla. Stat. 83.56(1)): NOT SETTLED" in options_part
          and "    step: the notice names the problem and says the tenant intends to end the lease because of it (83.56(1)): to do" in options_part
          and not re.search(r"\b[a-z]+(?:_[a-z]+)+\b", options_part)
          and "- Open or not: asked what they can do" in system_prompt())
finally:
    remove_scratch("t-smoke-options")

# a story no playbook covers (sheet.stop_text, lease.clauses_about): the stop lists what the tool covers and shows
# the lease's own clauses on the subject, word for word; nothing from the lease when no clause is on it
make_scratch("t-smoke-stop")
try:
    (MATTERS / "t-smoke-stop" / "m-001" / "events.jsonl").write_text("")
    load_matter("t-smoke-stop", "m-001")
    lease_pages = json.loads((record.matter_dir() / "pages.json").read_text())
    numbers = [c["number"] for c in lease_clauses(lease_pages)]
    check("the test lease splits into its numbered clauses, in order, a cross-reference not taken for one",
          len(numbers) == 78 and numbers[:3] == ["1.1", "1.2", "1.3"] and numbers[-1] == "22.2"
          and numbers.index("3.2") + 1 == numbers.index("3.3"))
    page_words = FOOTER.sub(" ", " ".join(" ".join(p["text"] for p in lease_pages).split()))
    def stop_for(story):
        record.matter["description"] = story
        return stop_text()
    roommate = stop_for("My roommate moved out in August and stopped paying his half of the rent. We're both on the lease.")
    printed_clauses = re.findall(r'page \d+: "(.*)"', roommate)
    check("a roommate story: the stop lists every covered situation and shows lease 21.3, word for word",
          roommate.startswith(STOP_LINE) and all(pb.description in roommate for pb in playbooks.values())
          and "Lease Section 21.3, Joint and Several Liability" in roommate
          and all(words.removesuffix(" ...") in page_words for words in printed_clauses))
    check("a towing story: the stop shows lease 5.4, Vehicles",
          "Lease Section 5.4, Vehicles" in stop_for("My apartment complex had my car towed from my parking spot."))
    check("a story the lease says nothing about: no lease part is shown",
          "Parts of your lease" not in stop_for("My landlord said he regrets renting to people like me because of my religion."))
finally:
    remove_scratch("t-smoke-stop")
check("the stop scratch matter is removed", not (MATTERS / "t-smoke-stop").exists())

make_scratch("t-smoke-playbooks")
try:
    load_matter("t-smoke-playbooks", "m-001")
    for issue in sorted(playbooks):
        record.matter.update(issues=[], proposed_issues=[], rejected_issues=[], facts={}, proposed={})
        record.add_issues([issue], "classify", "a smoke check")
        shown_sheet = io.StringIO()
        with contextlib.redirect_stdout(shown_sheet):
            run_sheet(answer_by_type(shown_sheet))
        listed = deadline_listing()
        clocks = [c.id for i in record.matter["issues"] if i in playbooks for c in playbooks[i].spec.clocks]
        dated = [d["clock"] for d in json.loads(listed)["deadlines"] if "deadline" in d] if not listed.startswith("Not yet") else []
        letter = draft_letter.invoke({"issue": issue, "posture": "preserve", "ask": "Confirm receipt of this letter",
                                      "respond_within_days": 10, "delivery_method": "certified mail"})
        check(f"{issue}: the sheet asks every fact, every clock gets a date, a letter carries its note",
              not pending_rows() and sorted(set(dated)) == sorted(set(clocks))
              and playbooks[issue].guidance["postures"]["notice_sufficiency"] in letter
              and f"issue: {issue}" in system_prompt())
finally:
    remove_scratch("t-smoke-playbooks")
check("the playbook scratch matter is removed", not (MATTERS / "t-smoke-playbooks").exists())
print()


# ---- The web page (app.py), run headless by Streamlit's AppTest on a scratch matter, with a stand-in model:
# open a saved matter, nothing new, a reply with a statute quote, a dollar amount, and a bad cite, a command,
# a proposed fact asked on the page's sheet with its related issue, the note that follows, a model error,
# and End session. AppTest runs the page in this same program, so the page and these checks share record.
logging.getLogger("streamlit").setLevel(logging.ERROR)     # AppTest's warnings about running outside a server
make_scratch("t-smoke-app", issues=["deposit_not_returned"], proposed={},
             facts={**json.loads((TEST_MATTER / "matter.json").read_text())["facts"], "claim_notice_received": False})
try:
    page = AppTest.from_file(str(Path(__file__).resolve().parent / "app.py"), default_timeout=60)
    page.run()
    listed = page.sidebar.selectbox[0]
    listed.select_index(listed.options.index("t-smoke-app / m-001")).run()
    next(b for b in page.sidebar.button if b.label == "Open").click().run()
    check("the page opens a saved matter from the list and starts a session",
          page.session_state["stage"] == "update" and record.matter["tenant"] == "t-smoke-app"
          and read_events()[-1]["kind"] == "session_started")
    said = "I got a letter from the landlord"
    stand_in = StandIn(messages=iter([
        AIMessage(content=f'Fla. Stat. 83.49(3)(a): "{FORFEIT}"\nSee also 83.64. You paid $900 *or more*.'),
        AIMessage(content="", tool_calls=[{"name": "propose_facts", "id": "a1", "args": {"facts_json": json.dumps(
            {"claim_notice_received": {"value": True, "how": "stated", "said": said}})}}]),
        AIMessage(content=f'You said: "{said}"'),
        AIMessage(content="", tool_calls=[{"name": "get_deadlines", "args": {}, "id": "a2"}]),
        AIMessage(content="")]))                            # asked only for the deadlines: nothing after the listing
    page.session_state["agent"] = create_agent(stand_in, tools=model_tools, checkpointer=InMemorySaver())
    page.session_state["config"] = {"configurable": {"thread_id": page.session_state["session"]}}
    next(b for b in page.button if b.label == "Continue").click().run()
    check("with nothing new and no fact open, the page goes straight to the chat", page.session_state["stage"] == "chat")
    page.chat_input[0].set_value("Was that legal?").run()
    bubbles = [(m.name, [x.value for x in m.markdown]) for m in page.chat_message]
    check("the page shows the model's reply in a speech bubble, the program's caution and line outside it",
          bubbles[-1][0] == "assistant" and "83\\.49\\(3\\)\\(a\\)" in bubbles[-1][1][0]
          and any("[Check: 83.64" in w.value.replace("\\", "") for w in page.warning)
          and any(READING_LINE in i.value.replace("\\", "") for i in page.info))
    check("the page shows a reply as written: a $ starts no math, a * no italics",
          "\\$900 \\*or more\\*" in bubbles[-1][1][0])
    page.chat_input[0].set_value("issues").run()
    check("a command typed on the page is answered by the program", page.session_state["history"][-1]["kind"] == "notice"
          and "deposit_not_returned: " in page.session_state["history"][-1]["text"])
    page.chat_input[0].set_value(said).run()
    check("after the model proposes a fact, the page shows the sheet with the suggestion filled in",
          page.session_state["stage"] == "sheet" and page.radio[0].value == "yes")
    next(b for b in page.button if b.label == "Save").click().run()
    page.radio[0].set_value("yes")
    next(b for b in page.button if b.label == "Save").click().run()
    while page.session_state["stage"] == "sheet":
        next(b for b in page.button if b.label == "Skip for now").click().run()
    check("the page's sheet confirms the fact, asks the related issue next, and leaves skipped facts open",
          record.matter["facts"]["claim_notice_received"] is True and "deposit_claim_received" in record.matter["issues"]
          and any(r["id"] == "claim_notice_date" for r in pending_rows()))
    page.chat_input[0].set_value("What are my deadlines?").run()
    lines = [json.loads(line) for line in (matter_dir() / "sessions" / f"{page.session_state['session']}.jsonl").read_text().splitlines()]
    check("what the sheet confirmed goes to the model with the next message, and the deadlines show in a program box",
          [line["text"] for line in lines if line["role"] == "program"][-1]
          == "[Program note: the tenant confirmed on the sheet: claim_notice_received = True, issue "
             "deposit_claim_received = confirmed]\n"
          and page.session_state["history"][-1]["kind"] == "deadlines")
    with contextlib.redirect_stderr(io.StringIO()):                 # the page prints the error's traceback
        page.chat_input[0].set_value("And now?").run()              # the stand-in has nothing left to say
    check("a model error is shown on the page as a caution, and the page goes on",
          page.session_state["history"][-1]["text"].startswith("[Check: the model could not be reached")
          and page.session_state["stage"] == "chat" and not page.exception)
    next(b for b in page.sidebar.button if b.label == "End session").click().run()
    check("End session logs the end and goes back to the start", page.session_state["stage"] == "door"
          and read_events()[-1]["kind"] == "session_ended" and record.session is None)
finally:
    remove_scratch("t-smoke-app")
check("the page's scratch matter is removed", not (MATTERS / "t-smoke-app").exists())
summary()
