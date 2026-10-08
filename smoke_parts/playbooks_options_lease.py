"""Smoke, part: Every playbook through the real code path, and the checks of items 72 to 84: the rules that apply only sometimes,
the lease profile's repairs clause, lease cites, options and what the tool knows of each condition, what the tool
does not know, the stop text, and the lease search.
Run by smoke.py, in order; each check prints a line, OK or FAIL."""
import contextlib
import io
import json
import re
import tempfile
from datetime import date, timedelta
from pathlib import Path
from langchain.messages import HumanMessage
import record
from checks import TEST_MATTER, check, make_scratch, remove_scratch
from config import MATTERS
from corpus import load_playbook, playbooks
from deterministic import check_options
from record import load_matter, read_events
from lease import lease_clauses, lease_text
from sheet import STOP_LINE, pending_rows, row_notes, run_sheet, stop_text
from prompt import RULES as RULES_TEXT
from prompt import LETTER_RULE, PARTS, options_status, system_prompt, unknowns_status
from replies import check_reply, cited_clause, cited_words
from tools import build_letter, deadline_listing, draft_letter, pretty, propose_facts
from tools import tools as model_tools
from smoke_parts.common import scripted

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
        for hint, answer in (("(YYYY-MM-DD)", "2026-10-31"), ("(yes/no)", "yes"), ("(amount)", "1200"), ("(words)", "a test answer"),
                             ("(number or words)", "1")):
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

# options before steps (TODO item 72), and what the tool knows of each condition (TODO item 81,
# deterministic.check_options): a condition is met through any of its ways, and is known (met, not met, not met yet),
# the tenant's to tell (a fact the sheet asks), the tenant's to check (a part of the lease the tool has not read, a
# code, a document), not settled (an open question), or outside the tool. Proved on three playbooks.
repair = playbooks["repair_not_made"]
today = date.today()
ac = {"problem_is_with": "the air conditioning", "single_family_or_duplex": False,
      "caused_by": "nothing anyone did (age, wear, weather)", "rent_paid_since_known": True, "wrote_to_landlord": True,
      "message_sent_by": "e-mail", "message_date": str(today - timedelta(days=30)), "message_mentions_ending": False,
      "message_mentions_rent": False, "message_words": "The AC is broken. Please fix it."}
roof = {**ac, "problem_is_with": "the roof", "rent_paid_since_known": False, "message_sent_by": "certified mail",
        "message_mentions_ending": True, "message_date": str(today - timedelta(days=10)),
        "message_words": "Please fix the roof within 7 days or I will end my lease because of it."}
read_profile = old_profile.model_copy(update={"maintenance_and_repairs": Clause(
    present=True, quote="7.2. Systems and Appliances. Landlord shall repair the heating, air -conditioning, electrical, and plumbing systems",
    page=4, section="ARTICLE 7")})
by_id = lambda pb, facts, profile=old_profile: {o["option"]: o for o in check_options(pb, facts, today, profile)}
ac_unread, ac_read = by_id(repair, ac), by_id(repair, ac, read_profile)
duty_unread, duty_read = ac_unread["end_the_lease"]["gates"][0], ac_read["end_the_lease"]["gates"][0]
check("item 81: an AC, the lease's repairs clause not read: ending the lease is not known yet, the tenant can check the lease or a code",
      ac_unread["end_the_lease"]["status"] == "not known yet" and duty_unread["state"] == "check"
      and [w["state"] for w in duty_unread["ways"]] == ["not met", "not met", "not met", "check", "check"]
      and "has not read the part of the lease on maintenance and repairs" in duty_unread["ways"][3]["why"]
      and "code enforcement office" in duty_unread["ways"][4]["why"]
      and duty_unread["if_met"] == "not settled" and ac_unread["end_the_lease"]["gates"][3]["state"] == "not settled")
check("items 81 and 86: the clause read: whether it promises this repair is the tenant's to check against it, never met on a sheet answer",
      duty_read["state"] == "check" and duty_read["ways"][3]["state"] == "check"
      and "Lease Article 7" in duty_read["ways"][3]["why"] and "an exception in it" in duty_read["ways"][3]["why"]
      and "lease_promises_repair" not in [e.id for e in repair.spec.elements])
check("item 81: withholding rent, which the lease does not reach, leaves a code to check",
      [w["state"] for w in ac_read["withhold_rent"]["gates"][0]["ways"]] == ["not met", "not met", "not met", "check"]
      and ac_read["withhold_rent"]["gates"][0]["if_met"] == "open")
roof_options, roof_soon = by_id(repair, roof), by_id(repair, {**roof, "message_date": str(today - timedelta(days=2))})
check("item 81: a roof leak is open; a notice by certified mail is delivered, its words the tenant's to check, so the 7 days are passed, not done",
      roof_options["end_the_lease"]["status"] == "open"
      and [s["status"] for s in roof_options["end_the_lease"]["steps"]] == ["done", "the tenant can check", "passed"]
      and [s["status"] for s in roof_soon["end_the_lease"]["steps"]] == ["done", "the tenant can check", "waiting"]
      and roof_options["end_the_lease"]["also_open"] == ["material_noncompliance"])
check("item 81: caused on the tenant's side closes both; a duplex leaves the lease to check; a fact not confirmed is the tenant's to tell",
      {o["status"] for o in by_id(repair, {**roof, "caused_by": "you"}).values()} == {"closed"}
      and by_id(repair, {**roof, "single_family_or_duplex": True})["end_the_lease"]["gates"][1]["state"] == "check"
      and by_id(repair, {k: v for k, v in roof.items() if k != "caused_by"})["end_the_lease"]["gates"][2]["state"] == "tell")
deposit = playbooks["deposit_not_returned"]
ghosted = {"tenancy_terminated": str(today - timedelta(days=60)), "vacated": str(today - timedelta(days=60)),
           "claim_notice_received": False, "forwarding_address_given": True, "early_or_periodic": False}
early = {**ghosted, "tenancy_terminated": str(today - timedelta(days=10)), "early_or_periodic": True, "leave_notice_given": False}
early_whole = by_id(deposit, early)["whole_deposit_back"]
check("item 81: the deposit: open when nothing came in 30 days; the 30 days still running is not met yet; a notice by certified mail closes it",
      by_id(deposit, ghosted)["whole_deposit_back"]["status"] == "open"
      and early_whole["gates"][1]["state"] == "not met yet" and early_whole["gates"][1]["if_met"] == "not known yet"
      and by_id(deposit, {**ghosted, "claim_notice_received": True, "claim_delivery": "certified mail"})["whole_deposit_back"]["status"] == "closed"
      and by_id(deposit, {k: v for k, v in ghosted.items() if k != "tenancy_terminated"})["whole_deposit_back"]["gates"][1]["state"] == "tell")
check("item 81: the deposit: left early without the 7-day notice leaves the lease's own notice term to check, with the clause the tool read",
      early_whole["status"] == "not known yet"
      and [w["state"] for w in early_whole["gates"][2]["ways"]] == ["not met", "not met", "not met", "not met", "check"]
      and "the tool has read the lease's clause on notice before moving out early" in early_whole["gates"][2]["ways"][4]["why"])
nonpayment = playbooks["notice_received_nonpayment"]
taped = {"nonpayment_notice_delivered": str(today - timedelta(days=8)), "premises_county": "Alachua", "rent_unpaid": True,
         "eviction_action_filed": False}
taped_options = by_id(nonpayment, taped)
orange = by_id(nonpayment, {**taped, "premises_county": "Orange", "eviction_action_filed": True})
check("item 81: a 3-day notice: the days passed close paying in time; no case filed leaves defending not open yet; the notice's form is the tenant's to check",
      taped_options["pay_within_three_days"]["status"] == "closed"
      and taped_options["defend_in_court"]["status"] == "not open yet"
      and taped_options["defective_notice_defense"]["gates"][0]["state"] == "check"
      and "the notice itself" in taped_options["defective_notice_defense"]["gates"][0]["why"])
check("item 81: a county with no court calendar is outside the tool; a case filed opens defending, with the registry step to do",
      orange["pay_within_three_days"]["status"] == "outside the tool"
      and "no court holiday calendar for Orange County" in orange["pay_within_three_days"]["gates"][0]["why"]
      and orange["defend_in_court"]["status"] == "open" and orange["defend_in_court"]["steps"][0]["status"] == "to do")
bad_way = (Path("playbooks") / "repair_not_made.yaml").read_text().replace(
    "- fact: rent_paid_since_known\n", "- fact: rent_paid_since_known\n              check: the lease\n", 1)
with tempfile.TemporaryDirectory() as tmp:
    (Path(tmp) / "bad.yaml").write_text(bad_way)
    try:
        load_playbook(Path(tmp) / "bad.yaml")
        refused = False
    except ValueError as e:
        refused = "exactly one of fact, clock, check, or outside" in str(e)
check("item 81: a way decided by two things is refused when the playbook loads", refused)

# the sheet asks what the tenant saw or did, never a legal call (TODO items 86 and 90 to 92, the student simulation of
# 2026-10-06): the tenant picks what the problem is with, who caused it, and how a message went, and copies its words;
# the playbook reads those answers against the statute, and what no answer settles is a check or an open question.
# The stories: F (an e-mail saying "I'm going to have to move out"), A (a portal request), C (hot water), E (a roommate).
from deterministic import compute_deadlines, matter_deadlines
from timeline import render_deadlines
story_f = {**ac, "message_date": str(today - timedelta(days=10)), "message_mentions_ending": True,
           "message_words": "If this isn't fixed I'm going to have to move out."}
f_end, f_keep = by_id(repair, story_f)["end_the_lease"], by_id(repair, story_f)["withhold_rent"]
f_listing = render_deadlines(json.dumps({"deadlines": matter_deadlines([repair], story_f, today)}, default=str))
check("items 90 to 92: an e-mail that mentions moving out is no done notice: its delivery and its words are the tenant's to check, the 7 days passed, not done",
      [s["status"] for s in f_end["steps"]] == ["the tenant can check", "the tenant can check", "passed"]
      and "83.505" in f_end["steps"][0]["why"]
      and "your words, as you gave them: \"If this isn't fixed I'm going to have to move out.\"" in f_end["steps"][1]["why"]
      and f_end["steps"][2]["why"] == "counts only if the steps above are done"
      and f_keep["steps"][0]["status"] == "not settled" and f_keep["steps"][1]["status"] == "to do")
check("items 90 to 92: the deadline from that e-mail is printed with what it counts only if",
      "seven days after termination notice" in f_listing
      and "counts only if your message was delivered in a way 83.56(4) allows and says you intend to end the lease" in f_listing)
portal = {**ac, "message_sent_by": "a resident portal request or message"}
check("items 90 to 92: a portal request that mentions neither ending the lease nor rent starts no 7-day period, and no notice step is done",
      [s["status"] for s in by_id(repair, portal)["end_the_lease"]["steps"]] == ["to do", "to do", "to do"]
      and compute_deadlines(repair, portal, today) == [])
hot = by_id(repair, {**roof, "problem_is_with": "hot water"})
pipes = by_id(repair, {**roof, "problem_is_with": "pipes, drains, toilets, or faucets"})
check("item 91: hot water is not settled under 83.51(1)(b), for both options, so withholding is never open on it; a leaking pipe is the plumbing",
      [w["state"] for w in hot["withhold_rent"]["gates"][0]["ways"]] == ["not met", "not settled", "not met", "check"]
      and hot["withhold_rent"]["status"] != "open" and hot["end_the_lease"]["gates"][0]["ways"][1]["state"] == "not settled"
      and pipes["withhold_rent"]["gates"][0]["state"] == "met")
mate, unsure = by_id(repair, {**roof, "caused_by": "a roommate"}), by_id(repair, {**roof, "caused_by": "I don't know"})
check("item 92: a roommate leaves the cause not settled under 83.51(4), closing neither option; not knowing who is the tenant's to check",
      [o["gates"][2]["state"] for o in mate.values()] == ["not settled", "not settled"]
      and "closed" not in {o["status"] for o in mate.values()}
      and unsure["end_the_lease"]["gates"][2]["state"] == "check"
      and "work order" in unsure["end_the_lease"]["gates"][2]["why"])
neighbor = playbooks["neighbor_disturbance"]
loud = {"source_rents_from_landlord": True, "complained_to_landlord": True, "complaint_in_writing": True,
        "complaint_sent_by": "handed to the landlord or the office", "complaint_mentions_ending": True,
        "complaint_words": "If the parties do not stop I will end my lease."}
loud_steps = by_id(neighbor, loud)["end_the_lease"]["steps"]
check("items 90 to 92: a neighbor complaint by hand is delivered, its words the tenant's to check; by the portal, to do; and it shares no fact with the repair notice",
      [s["status"] for s in loud_steps] == ["done", "the tenant can check"]
      and "I will end my lease" in loud_steps[1]["why"]
      and by_id(neighbor, {**loud, "complaint_sent_by": "a resident portal request or message"})["end_the_lease"]["steps"][0]["status"] == "to do"
      and {e.id for e in repair.spec.elements} & {e.id for e in neighbor.spec.elements} == {"landlord_response"})
bad_answer = (Path("playbooks") / "repair_not_made.yaml").read_text().replace("equals: [running water, hot water]",
                                                                               "equals: [running water, warm water]", 1)
with tempfile.TemporaryDirectory() as tmp:
    (Path(tmp) / "bad.yaml").write_text(bad_answer)
    try:
        load_playbook(Path(tmp) / "bad.yaml")
        refused = False
    except ValueError as e:
        refused = "names an answer problem_is_with does not list (warm water)" in str(e)
check("items 90 to 92: a way naming an answer its choice does not list is refused when the playbook loads", refused)
from sheet import parse_answer
answers = repair.spec.elements[1].choices
check("items 90 to 92: a choice is answered by its number or its words, spacing and capitals aside; anything else is refused",
      parse_answer("choice", "9", answers) == ("hot water", None) and parse_answer("choice", "  Hot   Water ", answers) == ("hot water", None)
      and parse_answer("choice", "18", answers) == (None, "a number from the list, or its words")
      and parse_answer("choice", "the water heater", answers)[0] is None)
# part 2 of the sheet asking plain facts (TODO item 102): the other playbooks ask how a paper went, where a fee is
# written, what the tenant did, and read the answers in their gates and steps
from deterministic import check_elements
dep, claim_pb, ending_pb, rent_pb, leave_pb = (playbooks[i] for i in ("deposit_not_returned", "deposit_claim_received",
                                                                       "lease_ending", "rent_increased", "wants_to_leave_early"))
came = lambda how: by_id(dep, {**ghosted, "claim_notice_received": True, "claim_delivery": how})["whole_deposit_back"]
check("item 102: a claim notice by regular mail leaves the whole deposit not settled, not closed; by certified mail closed; not known, to check",
      came("regular mail")["status"] == "not settled" and came("regular mail")["gates"][0]["state"] == "not settled"
      and came("certified mail")["status"] == "closed" and came("I don't know")["gates"][0]["state"] == "check")
left = lambda how: by_id(dep, {**early, "leave_notice_given": True, "leave_notice_sent_by": how})["whole_deposit_back"]["gates"][2]["ways"]
check("item 102: a notice before leaving early by certified mail is the tenant's to check against the 7 days; by e-mail, for the addendum too; by regular mail not a way 83.49(5) names",
      [w["state"] for w in left("certified mail")][1] == "check" and "7 days before you moved out" in left("certified mail")[1]["why"]
      and [w["state"] for w in left("e-mail")][2] == "check" and "83.505" in left("e-mail")[2]["why"]
      and [w["state"] for w in left("regular mail")][1:4] == ["not met", "not met", "not met"])
claim_facts = {"tenancy_terminated": str(today - timedelta(days=35)), "claim_notice_dated": str(today - timedelta(days=8)),
               "claim_notice_date": str(today - timedelta(days=5)), "objected": True}
objection = lambda how: by_id(claim_pb, {**claim_facts, "objection_sent_by": how})["object_to_claim"]["steps"][0]["status"]
notice_way = lambda how: by_id(claim_pb, {**claim_facts, "claim_delivery": how})["whole_deposit_back"]["gates"][1]["ways"][1]["state"]
check("item 102: an objection by letter to the notice's address is done, by e-mail not settled; a claim notice by certified mail is the way 83.49(3)(a) names, by regular mail not settled",
      objection("a letter mailed to the address the notice gives") == "done" and objection("e-mail") == "not settled"
      and notice_way("certified mail") == "not met" and notice_way("regular mail") == "not settled")
ended = lambda how: by_id(ending_pb, {"month_to_month": True, "period_end_date": str(today + timedelta(days=40)),
                                      "end_notice_given": True, "end_notice_sent_by": how})["end_month_to_month"]["steps"][0]["status"]
check("item 102: a notice ending a month-to-month tenancy by hand is done, by e-mail the tenant's to check, by text to do",
      [ended(h) for h in ("handed to the landlord or the office", "e-mail", "a text message")] == ["done", "the tenant can check", "to do"])
did = lambda **f: by_id(rent_pb, {"eviction_action_filed": True, **f})["retaliation_defense"]["gates"][0]["state"]
check("item 102: a complaint to a code office meets 83.64(1)'s example, a written repair notice is to check, another step or none not settled",
      did(complained_before_increase=True, complaint_kind=rent_pb.spec.elements[[e.id for e in rent_pb.spec.elements].index("complaint_kind")].choices[0]) == "met"
      and did(complained_before_increase=True, complaint_kind="a written notice to the landlord about a repair") == "check"
      and did(complained_before_increase=True, complaint_kind="something else") == "not settled"
      and did(complained_before_increase=False) == "not settled")
fee = lambda where: by_id(leave_pb, {"fee_in_writing": True, "fee_written_where": where})["early_termination_fee"]
gone = lambda how: by_id(leave_pb, {"leave_notice_given": True, "leave_notice_sent_by": how,
                                     "planned_move_out": str(today + timedelta(days=20))})["deposit_notice_before_leaving"]["steps"][0]
check("item 102: a fee written only in the lease closes the fee route, a separate paper meets it, not knowing is to check; a notice by certified mail is to check for its address, by text to do",
      fee("only in the lease itself")["status"] == "closed" and fee("in a separate paper I signed with the lease")["gates"][0]["state"] == "met"
      and fee("I don't know")["gates"][0]["state"] == "check"
      and gone("certified mail")["status"] == "the tenant can check" and "address" in gone("certified mail")["why"]
      and gone("a text message")["status"] == "to do")
check("item 102: one notice before moving out, asked once: the deposit and leaving-early playbooks share its facts",
      {"leave_notice_given", "leave_notice_sent_by"} <= {e.id for e in dep.spec.elements} & {e.id for e in leave_pb.spec.elements}
      and "about a similar problem" not in playbooks["notice_received_violation"].guidance["questions"]["prior_written_warning"])
old_answer = {"claim_delivery": "it came in the mail I think", "objected": False}
check("item 102: an old free-text answer to a question that is now a choice is asked again, and decides nothing",
      next(r for r in check_elements(claim_pb, old_profile, old_answer, {}) if r["id"] == "claim_delivery")["status"] == "missing"
      and by_id(claim_pb, {**claim_facts, **old_answer})["whole_deposit_back"]["gates"][1]["ways"][1]["state"] == "tell")

make_scratch("t-smoke-choice", issues=["repair_not_made"], proposed={},
             facts={k: v for k, v in {**story_f, "problem_description": "the AC blows warm air", "problem_started": "2026-09-10",
                                      "landlord_response": "nothing", "eviction_action_filed": False}.items() if k != "problem_is_with"})
try:
    load_matter("t-smoke-choice", "m-001")
    shown_sheet = io.StringIO()
    with contextlib.redirect_stdout(shown_sheet):
        run_sheet(scripted(["99", "Hot  Water"]))
    refused_answer = propose_facts.invoke({"facts_json": json.dumps({"caused_by": {"value": "my cat", "how": "stated", "said": "x"}})})
    letter = build_letter("Repair the air conditioning", 7, "certified mail", [])
    options_now = system_prompt().split("\n\n" + PARTS["options"] + ":\n")[1].split("\n\n")[0]
    check("items 90 to 92: the sheet lists a choice's answers by number, asks again for one not listed, and saves the words",
          "Which of these is the problem with? Pick the closest one. (number or words)" in shown_sheet.getvalue()
          and "    9. hot water" in shown_sheet.getvalue() and "Please type a number from the list, or its words" in shown_sheet.getvalue()
          and record.matter["facts"]["problem_is_with"] == "hot water")
    check("items 90 to 92: propose_facts refuses an answer the choice does not list",
          "caused_by: value must be a number from the list, or its words" in refused_answer)
    check("items 90 to 92: the letter's date line says when the tenant wrote, not that it was a notice",
          f"Message date: {pretty(story_f['message_date'])}" in letter and "notice date" not in letter.lower())
    check("items 90 to 92: the prompt gives each step's check with the tenant's words, the 7 days as passed if they count, and leaves out a way for another case",
          "    step: the notice names the problem and says the tenant intends to end the lease because of it (83.56(1)): the tenant can check: whether the words of your message" in options_now
          and "If this isn't fixed I'm going to have to move out." in options_now
          and "(83.56(1)): passed: counts only if the steps above are done" in options_now
          and "the problem is running water or hot water" in options_now
          and "the problem may be with the structure or the plumbing" not in options_now
          and "(counts only if your message was delivered in a way 83.56(4) allows" in system_prompt())
    reply_cautions = check_reply("Your message says \"If this isn't fixed I'm going to have to move out.\" Set those words "
                                 "beside Fla. Stat. 83.56(1). It also says \"I will end my lease on Friday\" (83.56(1)).", [])
    check("item 64: a whole reply quoting the tenant's own sentence beside 83.56(1) gets no caution; words the tenant never wrote still do",
          len(reply_cautions) == 1 and "\"I will end my lease on...\" (83.56(1)) is not in 83.56" in reply_cautions[0])
finally:
    remove_scratch("t-smoke-choice")
check("the choice scratch matter is removed", not (MATTERS / "t-smoke-choice").exists())
make_scratch("t-smoke-options", issues=["repair_not_made"], facts=ac, proposed={})
try:
    load_matter("t-smoke-options", "m-001")
    options_part = system_prompt().split("\n\n" + PARTS["options"] + ":\n")[1].split("\n\n")[0]
    check("item 81: the prompt gives each option's status, each condition's state and ways, and what follows, in words with no id",
          "End the lease because the landlord has not made the repair (Fla. Stat. 83.56(1)): NOT KNOWN YET" in options_part
          and "(83.56(1)): not known yet, met through any of these:" in options_part
          and "      - a building, housing, or health code where the unit is requires the landlord to fix it (83.51(1)(a)): not known yet, the tenant can check: " in options_part
          and "      if this condition is met, the option is not settled; if it is not, the option is closed" in options_part
          and "    step: the notice names the problem and says the tenant intends to end the lease because of it (83.56(1)): to do" in options_part
          and not re.search(r"\b[a-z]+(?:_[a-z]+)+\b", options_part)
          and "- Open or not: asked what they can do" in system_prompt())
    lease_row = {"kind": "fact", "status": "missing", "suggested": None, "lease_says": None,
                 "lease_clause": "maintenance_and_repairs"}             # a row whose question is about a lease clause
    unread_note = row_notes(lease_row)
    record.profile = read_profile
    check("item 81: the sheet shows the lease clause a question is about, or says the tool has not read it",
          unread_note == ["the tool has not read the part of your lease on maintenance and repairs: check your lease itself"]
          and row_notes(lease_row)[0].startswith("your lease's clause on maintenance and repairs (Lease Article 7), as the tool read it: \"7.2.")
          and "air -conditioning" in row_notes(lease_row)[0])
finally:
    remove_scratch("t-smoke-options")

# options for every playbook (TODO item 84): each has options, every status comes out on no facts, and the new kinds of
# way decide as they should: a way for a case the record does not show (applies_if), an open question alone, a fact
# whose own question does not apply; an undecided condition of an option another condition closes changes nothing
check("item 84: every playbook lists options, each with a status on no facts",
      all(pb.spec.options and {o["status"] for o in check_options(pb, {}, today, old_profile)} <= {"not known yet"}
          for pb in playbooks.values()))
claim = by_id(playbooks["deposit_claim_received"], {"tenancy_terminated": str(today - timedelta(days=35)),
              "claim_notice_dated": str(today - timedelta(days=8)), "claim_notice_date": str(today - timedelta(days=5)),
              "claim_delivery": "regular mail", "objected": False})
late_claim = by_id(playbooks["deposit_claim_received"], {"claim_notice_date": str(today - timedelta(days=20)), "objected": True})
check("item 84: a claim: objecting is open while the 15 days run; after them, an objection already sent is the tenant's to check against the date",
      claim["object_to_claim"]["status"] == "open" and claim["whole_deposit_back"]["gates"][1]["state"] == "check"
      and [w["state"] for w in late_claim["object_to_claim"]["gates"][0]["ways"]] == ["not met", "check"]
      and by_id(playbooks["deposit_claim_received"], {"claim_notice_date": str(today - timedelta(days=20)), "objected": False}
                )["object_to_claim"]["status"] == "closed")
dog = by_id(playbooks["notice_received_violation"], {"violation_notice_delivered": str(today - timedelta(days=8)),
            "notice_offers_cure": True, "notice_terminates_now": False, "prior_written_warning": False,
            "violation_corrected": False, "landlord_accepted_rent_after_notice": True, "eviction_action_filed": False})
check("item 84: a violation notice: the 7 days passed and nothing fixed closes the cure; an open question alone is not settled; rent taken leaves a check",
      dog["cure_the_violation"]["status"] == "closed"
      and dog["cure_the_violation"]["gates"][1]["ways"][1]["why"] == "it does not apply on the confirmed facts"
      and dog["contest_termination_notice"]["gates"][1]["state"] == "not settled"
      and dog["landlord_waived_by_rent"]["status"] == "not known yet")
shower = by_id(playbooks["landlord_entered_unannounced"], {"entry_notice_given": False, "tenant_consented": False,
               "emergency_claimed": False, "tenant_absent": False, "access_or_utilities_cut": False})
check("item 84: an entry with no notice: damages not known yet, the purpose not settled, the rest the tenant's to check; a lockout's damages closed",
      shower["entry_damages"]["status"] == "not known yet"
      and [g["state"] for g in shower["entry_damages"]["gates"]] == ["met", "met", "not settled", "check", "met", "met", "check"]
      and shower["prohibited_practice_damages"]["status"] == "closed")
check("item 84: a fact whose own question does not apply decides its way as not met (a stay asked of a tenant not planning one)",
      by_id(playbooks["lease_ending"], {"planning_to_stay": False})["stay_with_permission"]["gates"][0]["ways"][0]["why"]
      == "it does not apply on the confirmed facts")
make_scratch("t-smoke-closed", issues=["notice_received_violation"], proposed={},
             facts={"violation_notice_delivered": str(today - timedelta(days=8)), "notice_offers_cure": True,
                    "notice_terminates_now": False, "prior_written_warning": False, "violation_corrected": False,
                    "landlord_accepted_rent_after_notice": True, "eviction_action_filed": False})
try:
    load_matter("t-smoke-closed", "m-001")
    check("item 84: a condition of an option another condition closes is printed without what follows, and left out of what the tool does not know",
          "if this condition is met, the option is closed" not in options_status()
          and "of a nature the tenant should be given a chance to fix" not in unknowns_status()
          and "whether the violation did not go on after the rent was accepted" in unknowns_status())
finally:
    remove_scratch("t-smoke-closed")

# what the tool does not know (TODO item 83, prompt.unknowns_status): each point an option turns on that the tool has
# not decided, once, with its state and what it would change, in a prompt part after YOUR OPTIONS; rule 1 asks for it
# before any step, with "Not:" lines from three stories
make_scratch("t-smoke-unknown", issues=["repair_not_made", "notice_received_nonpayment"],
             facts={**ac, "nonpayment_notice_delivered": str(today - timedelta(days=1)), "premises_county": "Orange",
                    "rent_unpaid": True, "eviction_action_filed": False}, proposed={})
try:
    load_matter("t-smoke-unknown", "m-001")
    prompt_now = system_prompt()
    unknown_part = prompt_now.split("\n\n" + PARTS["unknown"] + ":\n")[1].split("\n\n")[0]
    check("item 83: the part comes after the options and names each point once, with its state and each option it decides",
          prompt_now.index(PARTS["options"]) < prompt_now.index(PARTS["unknown"]) < prompt_now.index(PARTS["deadlines"])
          and "- whether the lease says the landlord repairs this problem (83.56(1)) [repair not made]: the tenant can check: whether the lease's clause on maintenance and repairs says" in unknown_part
          and "(such as damage caused by a roommate or a guest); the tool has not read the part of the lease on maintenance and repairs" in unknown_part
          and unknown_part.count("- whether a building, housing, or health code where the unit is requires the landlord to fix it") == 1
          and "    Not pay rent because of the problem, and raise it as a defense if the landlord sues for possession: open if it holds; if not, closed" in unknown_part
          and "    End the lease because the landlord has not made the repair: not settled if it holds; if not, the condition turns on whether a building" in unknown_part
          and "[repair not made]: not settled: The tenant confirmed paying rent" in unknown_part)
    check("item 83: a county with no court calendar is outside the tool, a case not filed is not yet, and the lease parts not read are named; no id",
          "[notice received nonpayment]: outside the tool: not computed: no court holiday calendar for Orange County" in unknown_part
          and "- whether the landlord has filed an eviction case (83.60(2)) [notice received nonpayment]: not yet:" in unknown_part
          and "- the parts of the lease on maintenance and repairs: not read from this lease" in unknown_part
          and "search_lease searches the whole text" in unknown_part
          and not re.search(r"\b[a-z]+(?:_[a-z]+)+\b", unknown_part.replace("search_lease", "")))
    record.matter["facts"] = roof
    record.matter["issues"] = ["repair_not_made"]
    check("item 83: with every condition decided, the part holds only the lease lines",
          [line.split(":")[0] for line in unknowns_status().splitlines()]
          == ["- the parts of the lease on maintenance and repairs", "- anything else in the lease"])
finally:
    remove_scratch("t-smoke-unknown")
check("item 83: rule 1 asks for each point the tool does not know, as the part gives it, before any step, with Not lines from three stories",
      "When the answer turns on a point in WHAT THE TOOL DOES NOT KNOW, name it as that part gives it" in RULES_TEXT
      and "never such a point stated as a fact" in RULES_TEXT
      and all(story in RULES_TEXT for story in ("(a repair)", "(a deposit)", "(a 3-day notice)", "(a code the tool does not hold)")))

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
    page_words = " ".join(lease_text(lease_pages)[0].split())
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
        options_now = system_prompt().split("\n\n" + PARTS["options"] + ":\n")[1].split("\n\n")[0]
        check(f"{issue}: the sheet asks every fact, every clock gets a date, a letter carries its note, its options are in words",
              not pending_rows() and sorted(set(dated)) == sorted(set(clocks))
              and playbooks[issue].guidance["postures"]["notice_sufficiency"] in letter
              and f"issue: {issue}" in system_prompt()
              and all(f"- {o.label} (Fla. Stat. {o.cite}): " in options_now for o in playbooks[issue].spec.options)
              and not re.search(r"\b[a-z]+(?:_[a-z]+)+\b", options_now.replace("search_lease", "")))
finally:
    remove_scratch("t-smoke-playbooks")
check("the playbook scratch matter is removed", not (MATTERS / "t-smoke-playbooks").exists())
print()
