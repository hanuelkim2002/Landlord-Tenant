"""Smoke, part: the lease and the letters. The rules that apply only sometimes (rule 6 on letters), the system prompt without
the options layer's two parts (TODO item 113), the lease profile's repairs clause and the lease cites, the deadline a message
starts and what it counts only if, the letter (the program's lines around the tenant's account and request), the lease's
numbered clauses and the lease search, and every skill's clock facts through the real code path (proposed, confirmed,
dated, and a letter drafted).
Run by smoke.py, in order; each check prints a line, OK or FAIL."""
import contextlib
import io
import json
import re
from datetime import date, timedelta
from langchain.messages import HumanMessage
import record
from checks import TEST_MATTER, check, make_scratch, remove_scratch
from config import MATTERS
from deterministic import compute_deadlines, matter_deadlines
from record import load_matter, read_events
from lease import lease_clauses
from sheet import pending_rows, run_sheet
from prompt import RULES as RULES_TEXT
from prompt import CASE_RULE, LETTER_RULE, NO_CASES_RULE, PARTS, system_prompt
from replies import check_reply, cited_clause, cited_words
from skills import clock_facts, skills
from timeline import render_deadlines
from tools import build_letter, deadline_listing, draft_letter, pretty, propose_facts
from tools import tools as model_tools
from smoke_parts.common import prompt_part, scripted

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

# the options layer's two prompt parts are gone (TODO item 113); a loaded skill's "What the tenant can do" says what they said.
# With every skill loaded and a letter in play, neither name is in the prompt, the rules, or a tool's description.
make_scratch("t-smoke-nooptions")
try:
    load_matter("t-smoke-nooptions", "m-001")
    record.matter["skills"] = list(skills)
    every_prompt = system_prompt([HumanMessage(content="Can you write a letter to my landlord?")]) + CASE_RULE + NO_CASES_RULE
    gone = ("YOUR OPTIONS", "WHAT THE TOOL DOES NOT KNOW")
    check("item 113: the system prompt has no YOUR OPTIONS and no WHAT THE TOOL DOES NOT KNOW part, nor does a rule or a tool's "
          "description name one, and rule 1 sends the model to a loaded skill's \"What the tenant can do\"",
          not any(name in text for name in gone for text in [every_prompt, *(t.description for t in model_tools)])
          and not any(part.startswith(gone) for part in PARTS.values()) and not any(key in PARTS for key in ("options", "unknown"))
          and 'the loaded skill\'s "What the tenant can do"' in RULES_TEXT)
finally:
    remove_scratch("t-smoke-nooptions")
check("item 96: after a draft, rule 6 has the reply answer anything else asked with it, then the one line, never the letter retold",
      'after draft_letter, answer anything else the tenant asked in that message, as any answer, then end with "The '
      'letter appears above; tell me if you want changes." Never retell the letter.' in LETTER_RULE
      and "reply only" not in LETTER_RULE)


# the lease profile's repairs clause (TODO item 76): a profile read before the slot was added loads, with the slot
# not read (None) and left out of clauses(); the extraction asks for it; the prompt says the lease part is not the
# whole lease, and rule 2 forbids "the lease does not mention" from it
from lease import LeaseProfile
old_profile = LeaseProfile.model_validate_json((TEST_MATTER / "lease_profile.json").read_text())
check("item 76: an older profile loads with the repairs clause not read, and clauses() leaves it out; new reads ask for it",
      old_profile.maintenance_and_repairs is None
      and "maintenance_and_repairs" not in dict(old_profile.clauses()) and len(old_profile.clauses()) == 15
      and "air conditioning" in LeaseProfile.model_json_schema()["properties"]["maintenance_and_repairs"]["description"])
check("item 76: the lease part says it is not the whole lease, and rule 2 forbids saying the lease does not mention something",
      PARTS["lease"].startswith("YOUR LEASE (only the clauses the tool reads from the tenant's lease, not the whole lease")
      and 'Not: "The lease does not mention air conditioning."' in RULES_TEXT)

# lease cites (TODO item 77): YOUR LEASE gives each clause in words with the cite to use, no field name; the program
# prints the words for a section cite, a page cite (the clauses on that page with no number), and a cite inside an
# article
from lease import Clause, lease_cite, lease_lines
article = Clause(present=True, quote="7.1. Statutory Duties. ...", page=4, section="ARTICLE 7")
lines_now = lease_lines(old_profile)
check("item 77: YOUR LEASE names each clause in words with its cite, and no field name",
      "- the rent (cite as Lease Section 3.1): " in lines_now and "- the tenants' names (cite as Lease, page 1): " in lines_now
      and "- maintenance and repairs: not read from this lease" in lines_now
      and not re.search(r"\b[a-z]+(?:_[a-z]+)+\b", lines_now)
      and lease_cite(article) == "Lease Article 7" and cited_clause(article, "7.2", "")
      and not cited_clause(article, "17.2", "")
      and 'Not: "(Lease notice_before_vacating)" or "(term_end)"' in RULES_TEXT)

# the deadline a message starts and what it counts only if (TODO items 90 to 92, the student simulation of 2026-10-06): a repair
# message sent by e-mail that says "I'm going to have to move out" starts the 7 days of 83.56(1), printed with what the date
# counts only if (the tool does not decide whether the message was delivered in a way 83.56(4) allows or says the tenant
# intends to end the lease); a message that mentions neither ending the lease nor rent starts no 7-day period at all.
today = date.today()
repair_skill = skills["repair_not_made"]
email_message = {"message_date": str(today - timedelta(days=10)), "message_mentions_ending": True, "message_mentions_rent": False}
email_listing = render_deadlines(json.dumps({"deadlines": matter_deadlines([repair_skill], email_message, today)}, default=str))
check("items 90 to 92: the deadline from an e-mail that mentions moving out is printed with what it counts only if",
      "seven days after termination notice" in email_listing
      and "counts only if your message was delivered in a way 83.56(4) allows and says you intend to end the lease" in email_listing)
check("items 90 to 92: a message that mentions neither ending the lease nor rent starts no 7-day period",
      compute_deadlines(repair_skill, {**email_message, "message_mentions_ending": False}, today) == [])
make_scratch("t-smoke-notice", skills=["repair_not_made"], proposed={}, facts=email_message)
try:
    load_matter("t-smoke-notice", "m-001")
    letter = build_letter("", "Please repair the air conditioning.", 7, "certified mail", "Jordan Ellis", [])
    check("items 90 to 92: a letter has no date line from the record, so none says the tenant's message was a notice",
          "Message date" not in letter and "notice date" not in letter.lower())
    check("items 90 to 92: the prompt gives the 7 days from the message with what they count only if",
          "(counts only if your message was delivered in a way 83.56(4) allows" in system_prompt())
    said = [HumanMessage(content="I e-mailed them: If this isn't fixed I'm going to have to move out.")]   # the tenant's words
    reply_cautions = check_reply("Your message says \"If this isn't fixed I'm going to have to move out.\" Set those words "
                                 "beside Fla. Stat. 83.56(1). It also says \"I will end my lease on Friday\" (83.56(1)).", said)
    check("item 64: a whole reply quoting the tenant's own sentence beside 83.56(1) gets no caution; words the tenant never wrote still do",
          len(reply_cautions) == 1 and "\"I will end my lease on...\" (83.56(1)) is not in 83.56" in reply_cautions[0])
finally:
    remove_scratch("t-smoke-notice")
check("the notice scratch matter is removed", not (MATTERS / "t-smoke-notice").exists())

# the letter (TODO 95): the program's lines around the tenant's account and request, each printed as written, never
# inside a sentence of the program's; a date or an amount the record does not hold is named under the letter; a cite in
# the tenant's part, or a signer the lease does not name, is refused
make_scratch("t-smoke-letter", skills=["repair_not_made"], proposed={},
             facts={"problem_started": "2026-09-10", "message_date": "2026-09-26"})
try:
    load_matter("t-smoke-letter", "m-001")
    record.start_session("existing")
    record.append_transcript({"role": "tenant", "text": "the tech came sept 19 and its like 87 in here"})
    signer = "Jordan Ellis"                               # the test lease names "JORDAN A. ELLIS , an individual"
    letter = build_letter("The air conditioning stopped working on September 10, 2026.",
                          "I, Morgan Davis, am ending my lease", 3, "by hand to the leasing office", signer, [])
    fact_ids = {*record.matter["facts"], *(fact for s in skills.values() for fact in clock_facts(s))}
    labels = {f"{fact.replace('_', ' ').capitalize()}:" for fact in fact_ids}
    check("item 95: the account and the request are printed as written, the delivery line once, no date line from the "
          "record, the signer's name alone, and dates as a letter writes them",
          "\n\nThe air conditioning stopped working on September 10, 2026.\n\nI, Morgan Davis, am ending my lease.\nPlease respond by " in letter
          and "I request that you" not in letter and "\nDelivery: by hand to the leasing office\n" in letter
          and "by by" not in letter and not any(label in letter for label in labels) and letter.endswith("\n\nJordan Ellis")
          and pretty("2026-10-06") == "October 6, 2026")
    drafts_before = sum(ev["kind"] == "draft" for ev in read_events())
    args = {"issue": "repair_not_made", "posture": "preserve", "request": "Please repair the air conditioning.",
            "respond_within_days": 7, "delivery_method": "certified mail", "signed_by": signer}
    known = draft_letter.invoke({**args, "account": "It stopped on September 10. A technician came on Sept. 19. "
                                                    "My deposit was $1,850.00."})
    unknown = draft_letter.invoke({**args, "account": "It stopped on September 10. Seven days after my message was "
                                                      "October 3, and I paid $1,278."})
    check("item 95: dates and amounts from the sheet, the tenant's messages, and the lease pass; ones the record does "
          "not hold are named under the letter, not in it",
          "CHECK BEFORE YOU SEND" not in known
          and "\n\n[CHECK BEFORE YOU SEND, not part of the letter: the tool did not find October 3 and $1,278 in your "
              "answers, your messages, or your lease. Make sure each is right.]" in unknown and "NOTE TO TENANT" not in unknown
          and "CHECK BEFORE YOU SEND" not in (record.matter_dir() / read_events()[-1]["file"]).read_text())
    refused = [draft_letter.invoke({**args, "account": a}) for a in ("Under 83.51(1) you must fix it.",
                                                                     "Lease Section 7.2 says so.")]
    signers = [draft_letter.invoke({**args, "account": "", "signed_by": s})
               for s in ('Jordan A. Ellis ("Tenant")', "Morgan Davis", "")]
    check("item 95: a cite in the tenant's part, a signer the lease does not name, one with a label, and none are "
          "refused, and nothing is drafted",
          all(r.startswith("Rejected: the account or the request cites") for r in refused)
          and all(r.startswith("Rejected: signed_by must be a tenant the lease names") for r in signers)
          and sum(ev["kind"] == "draft" for ev in read_events()) == drafts_before + 2)
    record.end_session()
finally:
    record.session = None
    remove_scratch("t-smoke-letter")
check("the letter scratch matter is removed", not (MATTERS / "t-smoke-letter").exists())

# the test lease's numbered clauses (lease.lease_clauses): the lease search, the words a reply cites, and the lease
# cites all read the lease split at its headings
make_scratch("t-smoke-clauses")
try:
    load_matter("t-smoke-clauses", "m-001")
    lease_pages = json.loads((record.matter_dir() / "pages.json").read_text())
    numbers = [c["number"] for c in lease_clauses(lease_pages)]
    check("the test lease splits into its numbered clauses, in order, a cross-reference not taken for one",
          len(numbers) == 78 and numbers[:3] == ["1.1", "1.2", "1.3"] and numbers[-1] == "22.2"
          and numbers.index("3.2") + 1 == numbers.index("3.3"))
finally:
    remove_scratch("t-smoke-clauses")
check("the clauses scratch matter is removed", not (MATTERS / "t-smoke-clauses").exists())

# the lease search (TODO item 82): the model searches the whole lease text before it says the lease lacks something;
# the test lease's holdover clause (2.4) and late charge (3.3), which the profile does not hold, are found through the
# PDF's broken words, a phrase found nowhere says so, and a reply citing a found clause gets its words printed
from tools import search_lease
make_scratch("t-smoke-lease")
try:
    (MATTERS / "t-smoke-lease" / "m-001" / "events.jsonl").write_text("")
    load_matter("t-smoke-lease", "m-001")
    holdover = next(c for c in lease_clauses(record.lease_pages()) if c["number"] == "2.4")
    check("item 82: the running header comes off each page with no word of the lease (Section 2.4 reads whole)",
          "become month -to-month on the same terms, terminable by either Party" in holdover["text"]
          and "Page 2 of 12" not in holdover["text"])
    found = {phrase: search_lease.invoke({"phrase": phrase}) for phrase in ("holdover", "late charge", "air conditioning", "hot tub")}
    check("item 82: search_lease finds the holdover clause, the late charge, and the air-conditioning repair, which the profile does not hold",
          "- Lease Section 2.4, Month -to-Month Holdover With Consent, page 1: \"If Landlord accepts Rent" in found["holdover"]
          and "- Lease Section 3.3, Late Charge, page 2:" in found["late charge"]
          and "- Lease Section 7.2, Systems and Appliances, page 4:" in found["air conditioning"]
          and not any(name == "maintenance_and_repairs" for name, _ in record.profile.clauses()))
    check("item 82: a phrase found nowhere in the lease's text says so, and asks for another wording; each search is logged",
          found["hot tub"].startswith("No clause or page of the lease's text (12 pages) holds \"hot tub\"")
          and "try another wording" in found["hot tub"]
          and [ev.get("lease_search") for ev in read_events() if ev["kind"] == "fetch"] == list(found))
    printed = cited_words("Your lease turns month to month if the landlord takes rent after the term (Lease Section 2.4), "
                          "and the deposit comes back as the lease says (Lease Section 4.3). See also Lease Article 7.")
    check("item 82: a reply citing a clause the profile does not hold gets its words printed from the lease's text; a held one only from the profile",
          "Lease Section 2.4, page 1 (Month -to-Month Holdover With Consent): If Landlord accepts Rent" in printed
          and "Lease Section 7.2, page 4 (Systems and Appliances): Landlord shall repair the heating" in printed
          and "Lease Section 4.3, page 2 (notice before moving out early)" in printed
          and "(Return of Deposit and Claims)" not in printed)
    nbsp = cited_words("The landlord must repair the air conditioning (Lease Section\u202f7.2), and see Fla. Stat.\u00a083.60\u00a0(1)(b).")
    check("item 85: a cite written with a no-break space still gets its words printed (lease and statute)",
          "Lease Section 7.2, page 4 (Systems and Appliances)" in nbsp and "Fla. Stat. 83.60(1)(b):" in nbsp)
    check("item 82: rule 2 asks for a search before saying the lease lacks something, and the model has the tool",
          "call search_lease first" in RULES_TEXT and "search_lease" in [tl.name for tl in model_tools]
          and "search_lease searches the whole lease's text" in PARTS["lease"])
finally:
    remove_scratch("t-smoke-lease")

# ---- Every skill's clock facts through the real code path (item 112), on a scratch matter: for each of the ten skills,
# the model proposes its clock facts (a date for every date, yes for every applies_if, a county with a stored court holiday
# calendar), the confirmation accepts each, every clock gets a date, nothing is left waiting, and a letter can be drafted.
# A new skill is covered without a new check.
ANSWERS = {"date": ("2026-10-31", "2026-10-31"), "bool": (True, "yes"), "county": ("Alachua", "Alachua")}    # value, tenant's words
make_scratch("t-smoke-clocks")
try:
    load_matter("t-smoke-clocks", "m-001")
    record.start_session("existing")
    record.append_transcript({"role": "tenant", "text": "It all happened on 2026-10-31 in Alachua, and the answer to each question is yes."})
    for name in sorted(skills):
        record.matter.update(skills=[], facts={}, proposed={})
        record.add_skill(name)
        typed = clock_facts(skills[name])
        if typed:
            propose_facts.invoke({"facts_json": json.dumps({fact: {"value": ANSWERS[kind][0], "how": "stated", "said": ANSWERS[kind][1]}
                                                            for fact, kind in typed.items()})})
        proposed_all = {r["id"]: r["type"] for r in pending_rows()}
        with contextlib.redirect_stdout(io.StringIO()):
            run_sheet(scripted([""] * len(typed)))
        listed = deadline_listing()
        clocks = [c.id for c in skills[name].clocks]
        dated = [d["clock"] for d in json.loads(listed)["deadlines"] if "deadline" in d]
        letter = draft_letter.invoke({"issue": name, "posture": "preserve", "account": "",
                                      "request": "Please confirm receipt of this letter.", "respond_within_days": 10,
                                      "delivery_method": "certified mail", "signed_by": "Jordan Ellis"})
        check(f"{name}: its clock facts are proposed and confirmed, every clock gets a date, nothing waits, a letter is "
              "drafted with nothing added under it, its instructions are in the prompt",
              proposed_all == typed and not pending_rows() and not record.matter["proposed"]
              and record.matter["facts"] == {fact: ANSWERS[kind][0] for fact, kind in typed.items()}
              and sorted(set(dated)) == sorted(set(clocks)) and "waiting" not in json.loads(listed)
              and "Please confirm receipt of this letter." in letter and "NOTE TO TENANT" not in letter
              and f"# {name}\n" in prompt_part("loaded"))
    record.end_session()
finally:
    record.session = None
    remove_scratch("t-smoke-clocks")
check("the clocks scratch matter is removed", not (MATTERS / "t-smoke-clocks").exists())
print()
