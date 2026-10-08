"""Smoke, part: Each piece checked on its own, on the test matter in memory (nothing written): the playbook checks, element
status and deadlines with a fixed today, court business days, the case corpus and the case wiki, a lease value next
to a tenant's, the letter template, cites and quotes in a reply, a reply that is not JSON at intake, and both
timelines.
Run by smoke.py, in order; each check prints a line, OK or FAIL."""
import json
import re
import shutil
import tempfile
from datetime import date
from pathlib import Path
import PyPDF2
from langchain.messages import AIMessage
import record
from calendars import court_calendars
from checks import check
from citations import SUBSECTION_START, check_cites, check_quoted, cites_without_quote, quoted_passages, subsections
from config import CASES, WIKI
from corpus import check_all_playbooks, load_playbook, playbooks, statute
from deterministic import NOT_JSON, ask_json, check_elements, compute_deadlines, lease_value
from dev.build_cases import court_text
from wiki import lint, read_pages, verified, verify
from record import list_matters, load_matter
from timeline import render_deadlines, render_timeline
from tools import build_letter, deadline_listing
from smoke_parts.common import FORFEIT

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
# read_pages reuses the pages it parsed while no file changes, and reads a page again once it is written
first_read, second_read = read_pages(wiki_copy), read_pages(wiki_copy)
fees = wiki_copy / "topics" / "Fees and costs in a suit over the deposit.md"
fees_text = fees.read_text()
fees.write_text(fees_text + "\n")
after_write = read_pages(wiki_copy)
check("the wiki's pages are parsed once and reused, and read again after a page is written",
      second_read is first_read and after_write is not first_read
      and after_write["Fees and costs in a suit over the deposit"]["body"].endswith("\n\n"))
fees.write_text(fees_text)
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
# TODO item 64: a quote is held to the cite next to it only when its words are the statute's; someone else's words
# that the model was given (the tenant's, the lease's, a case's, the tool's own) pass beside any cite
CASE_WORDS = "untimely notice forfeited their right to impose any claim upon appellant’s security deposit"   # 573 So. 2d 76
MOVE_OUT = "If this isn't fixed I'm going to have to move out."                     # the tenant's e-mail (student story F)
LEASE_WORDS = "Tenant shall notify Landlord in writing of a forwarding address"
POSTURE = "Adds the 83.51(1) duty, quoted."
given_now = "\n".join([CASE_WORDS, MOVE_OUT, LEASE_WORDS, "assert: " + POSTURE, statute["83.49"]])
check("item 64: the tenant's words, the lease's, a case's, and the tool's own pass next to a statute cite they are not from",
      check_quoted(f'Your e-mail says "{MOVE_OUT}" Set that beside Fla. Stat. 83.56(1).', given_now) == []
      and check_quoted(f'Lease Section 4.3: "{LEASE_WORDS}" (Fla. Stat. 83.49(3)(a))', given_now) == []
      and check_quoted(f'The court said the landlords\' "{CASE_WORDS}" (83.49(3)(a))', given_now) == []
      and check_quoted(f'assert: "{POSTURE}" (Fla. Stat. 83.51(1))', given_now) == [])
check("item 64: statute words cited to the wrong section, and words found nowhere, are still flagged though the model was given text",
      check_quoted(f'"{FORFEIT}" (83.56)', given_now)[0][2] == "is not in 83.56; it is in 83.49"
      and check_quoted(f'"{FORFEIT}" (83.49(3)(b))', given_now)[0][2] == "is in 83.49(3)(a), not 83.49(3)(b)"
      and check_quoted('"Unless the tenant objects in writing within 15 days" (83.49(3)(b))', given_now)[0][2] == "is not in 83.49")
# a legal bracket marks the quoter's alteration ("[t]he", "specif[y]"): set aside as an ellipsis is, the words around
# it must still be word for word, and the cite check still holds
INTENT = "the noncompliance and indicat[e] the intention of the tenant to terminate the rental agreement"
check("brackets: a statute quote and a case quote with bracketed alterations pass",
      check_quoted(f'"specif[y] {INTENT}" (83.56(1))', "") == []
      and check_quoted(f'"{CASE_WORDS.replace("appellant’s", "[the tenant’s]")}"', given_now) == []
      and check_quoted(f'"[h]{FORFEIT[1:]}" (Fla. Stat. 83.49(3)(a))', "") == [])
check("brackets: a word changed outside the brackets, and a bracketed quote cited to the wrong subsection, are still flagged",
      check_quoted(f'"specif[y] {INTENT.replace("indicat[e]", "indicates")}" (83.56(1))', "")[0][2] == "is not in 83.56"
      and check_quoted(f'"[h]{FORFEIT[1:]}" (83.49(3)(b))', "")[0][2] == "is in 83.49(3)(a), not 83.49(3)(b)")
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
