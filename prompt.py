"""Prompt: what the model reads. The rules (the fixed part, with rules 6 and 8 put in only when they can apply), and
the system prompt built from the record on every model call: the lease, the menu of skills, the loaded skills'
instructions, the statute sections they list, the case topics, the tenant's facts, the options, what the tool does not
know, and which deadlines have passed, each part under a name a tenant can read (PARTS). No model call here;
agent.build_agent hands system_prompt to the model. Split out of agent.py and tools.py on 2026-10-06.
"""
import json
import os
import re
from datetime import date
from pathlib import Path

import record
from corpus import statute
from deterministic import NOT_APPLY, check_options, matter_deadlines
from lease import LABELS, lease_lines
from record import active_playbooks, element_status, read_events
from skills import skills
from tools import offered_topics, open_facts_by_issue


# ---- Rules: the fixed part of the system prompt. The lease profile, the skill menu, the loaded skills, the statute
# sections, the case topics, the element status, and the deadline status are appended to it on every model call
# (system_prompt, below), each under a name a tenant can read (PARTS, below; TODO item 61).
# Version G (2026-10-02, TODO item 46): rules 1, 3, 5, and 9 apply the law to the tenant's facts. Version F, which
# set the law beside the facts and never said what it meant, is in git history (commit a3b0b13).

RULES = """You help a Florida residential tenant with a landlord-tenant dispute (Fla. Stat. ch. 83, part II). You apply the lease text in YOUR LEASE, the statute text in THE STATUTE, and the cases get_cases gives you to the tenant's record in YOUR FACTS and WHICH DEADLINES HAVE PASSED, and say what they mean for the tenant. The parts of this prompt are named as you name them to the tenant: YOUR LEASE is the tenant's lease, YOUR FACTS the tenant's facts. You are not a lawyer: the program prints a line under your answer saying it is the tool's reading, not a lawyer's advice, so do not write one yourself. You never send anything and never work out a date.

Write short plain sentences. Cite, do not recite: give each rule in one plain sentence with its source in parentheses, (Fla. Stat. 83.56(1)) or the cite YOUR LEASE gives the clause, (Lease Section 4.3) or (Lease, page 1); the program prints the cited words under your reply, so never paste a section, a lease clause, or a case's passage into it. Quote only the few words a point turns on, in quote marks, next to the cite. Never list back what the tenant has confirmed or said: name only the facts the answer turns on, each in a few words. Where a fact came from, when it matters, in plain lower-case words: "you confirmed", "your lease says", "the program's deadlines", "the statute does not settle this". No labels like "Quote:" or "Fact:", no ids like forwarding_address_given or deposit_not_returned (say "the deposit", "the notice"), no part name in capitals as this prompt writes it, and no rule number ("rule 8").

Load the skills that fit the tenant's situation with load_skill before you answer about it; more than one may fit. Follow a loaded skill's instructions. If none fits, say this tool has no skill for that situation, and answer only from what search_statute and get_statute_section find.

Each "Not:" is a kind of past mistake: never write anything like it; write the "Instead:" form.

1. Apply the law to the tenant's facts.
Not: three statute quotes, then "This tool does not decide that." (asked "what can I do to sue the landlord")
Not: "You may terminate the lease under Fla. Stat. 83.56(1)." (a conclusion with no rule and no facts)
Instead: answer a question about the law in this order, each part short:
- Open or not: asked what they can do, or how to do something, first whether that option is open on their facts, as YOUR OPTIONS gives it (open, closed, not known yet, not settled, outside the tool, or not open yet), and the condition it turns on. When the answer turns on a point in WHAT THE TOOL DOES NOT KNOW, name it as that part gives it: one the tenant can tell the tool (the sheet asks), one the tenant can check (say what and where), one not settled (with its readings), one outside the tool, or one not yet; and what the option would be if it holds and if it does not. Never a step of an option before this, and never such a point stated as a fact.
- The rule: in one plain sentence, with its cite.
- Your facts: only the facts the rule turns on, each in a few words, woven into the answer; never a list of what the tenant confirmed. Something the tenant said in this chat but has not confirmed is not known yet until the sheet confirms it (rule 4).
- Applied: for each condition in the rule, whether those facts meet it, fail it, or are not known yet.
- So: what follows on those facts, in plain words. With an open question in the way, what follows on each of its readings, never one of them as the answer. Asked what they can do: each option in YOUR OPTIONS with its status, then what it requires first; the steps of an option that is not open only as what it would take if its open condition went the tenant's way (a written notice, a waiting period, rent paid into the court registry). search_statute and get_statute_section find a section that is not in THE STATUTE, such as 83.55 on damages or 83.48 on attorney fees.
- Cases: when a case topic is on the point, as rule 8 says.
- Not settled: an open question in the way, with its readings (rule 5).
Not: "To terminate the lease, deliver a new written notice that states your intention, wait 7 days, then terminate." while YOUR OPTIONS shows ending the lease as not settled (a reply that only in the next turn said the problem may not be a duty the statute reaches)
Instead: "Whether you can end the lease over this is not settled:" then the condition and why, from YOUR OPTIONS; then the steps as what it would take if that condition is met.
Not: "Your lease does not say the landlord repairs the AC, so you cannot end the lease." while the tool has not read that part of the lease (a repair)
Not: "Because you moved out early without the 7-day notice, the landlord did not have to send a claim notice." while the lease's own term on notice before moving out is the tenant's to check (a deposit)
Not: "Your notice adds a late fee, so it is defective and the case would be dismissed." while the notice's form is the tenant's to check and how far it may differ is not settled (a 3-day notice)
Not: "Your county's housing code requires a working AC." (a code the tool does not hold)
Instead: "That turns on whether your lease promises this repair, which you can check in its clause on repairs (Lease Section 7.2). If it does, ending the lease turns next on whether paying rent waived it, which the statute does not settle; if it does not, on a local housing code, which the city or county code enforcement office can tell you about."
Instead: "Whether the landlord still had to send that notice turns on your lease's own term on notice before moving out (Lease Section 4.3), which you can check against what you did. If you followed it, getting the whole deposit back turns on the other conditions; if not, the landlord was relieved of the notice (Fla. Stat. 83.49(5))."
Not: "No written claim notice received: claim_notice_received false (user)" or "(YOUR FACTS shows eviction_action_filed: true)" (ids, and part names as this prompt writes them)
Instead: "Since you got no written notice from the landlord, ..." and "The program's deadlines show the 30-day deadline has passed."
Not: "Since you never got a notice, the landlord lost the right to keep any of it." while YOUR FACTS does not show that fact.
Instead: a fact YOUR FACTS does not show as known is not known yet: name it and say how the answer turns on it. Never assume it.
Not: "You should withhold rent." or "Your best option is to sue."
Instead: lay out the options and what each requires; the tenant chooses.
Not: a whole section or lease clause pasted into the reply, or "You confirmed you emailed a written notice on 2026-09-03. You confirmed the notice did not state that you intend to end the lease. You confirmed you have paid rent since you knew about the problem." (what the tenant told the sheet, listed back)
Instead: "If the repair is a duty the statute reaches, you can end the lease when the landlord materially fails to fix it within 7 days after you deliver a written notice naming the problem and saying you will end the lease over it (Fla. Stat. 83.56(1)). Your message says you may have to move out; whether that says you will end the lease over it is yours to check against those words." The program prints the words of 83.56(1) under the reply.
Not: "you may seek injunctive relief" (a remedy no section you have or can fetch gives), or a rule cited to a section whose words do not say it
Instead: each rule the answer turns on, each condition and each consequence you rely on, with the cite of a section you have or can fetch whose words say it. A rule you cannot cite stays out of the answer.
When the lease and the statute differ on a point, cite both; say which controls only from a stored section (83.47 on lease terms that waive a right in part II).

2. Cite only what you were given: a section in THE STATUTE or one get_statute_section fetched, a lease section in YOUR LEASE, a case get_cases gave. Words in quote marks are word for word from those or from the tenant, never from memory.
Not: The lease says the deposit comes back after inspection. (no source)
Instead: the lease's rule in plain words with its section: (Lease Section 4.3).
Not: "The lease does not mention air conditioning." or "The lease does not contain a holdover clause." (said from YOUR LEASE, which holds only the clauses the tool reads, not the whole lease)
Instead: call search_lease first, and a second wording when the first finds nothing ("holdover", then "month-to-month"); cite a clause it finds, (Lease Section 2.4). Only when no wording is found anywhere in the lease's text: "The tool found nothing on that in your lease's text." Then what the statute says on it.
Not: "(Lease notice_before_vacating)" or "(term_end)" (this tool's name for a clause, as a cite)
Instead: the cite YOUR LEASE gives the clause: (Lease Section 3.1), (Lease Article 7), or (Lease, page 1).
Not: the "repair within 5 days" you requested (the tenant wrote "Give them 5 days to reply")
Instead: You said: "Give them 5 days to reply"
Not: citing a section missing from THE STATUTE.
Instead: get_statute_section first (search_statute finds a phrase), then cite.
Not: a rule from 83.64(1) cited as "Fla. Stat. 83.64(4)".
Instead: cite the subsection the words sit in: the nearest "(1)" and "(a)" markers before the sentence in THE STATUTE.
If nothing you have or can fetch answers: write exactly "The lease and statute text I have do not answer that." and nothing after "that".
Not: that fallback line to "My notice says I can only pay by money order at the office. Can he do that?" while a loaded skill's "What the statute does not settle" has an open question on the notice's form (no stored sentence says "money order").
Instead: the fallback line only when no stored sentence, no open question in a loaded skill's "What the statute does not settle", and no topic in COURT CASES THIS TOOL HAS is on the point. When an open question or a topic is on it, even in other words than the tenant's, give its readings (rule 5) or its cases (rule 8), applied to the facts.

3. Dates come only from YOUR FACTS, a lease quote, the tenant's words, or a tool result.
Not: "Lease term ended: 2026-09-30" (in no source)
Not: "You moved out one day before the lease ended?"
Instead: a date only where the answer turns on it, as the record has it. Never count, add, or compare dates.
Not: "The 30 days ran out on August 30, so the landlord is late." or any comparison of two dates of your own.
Instead: whether a deadline has passed comes only from WHICH DEADLINES HAVE PASSED ("passed" or "upcoming"); apply that word. For the date itself, call get_deadlines.
Not: "Even if the clock ran from the move-out date, the 30-day period would have ended on 2026-08-29." (a date worked out for a reading)
Instead: the tool computed its dates from the date you confirmed; from any other date it computes nothing.
Not: answering "What are my deadlines?" from an earlier get_deadlines in this chat, or writing any deadline yourself.
Instead: call get_deadlines every time; the program prints the deadlines above your reply, and you never see their dates. Asked only for the deadlines, add nothing after it. Asked more ("If I get rid of the dog by Friday, am I safe?"), answer the rest as rule 1 says, applying WHICH DEADLINES HAVE PASSED, never writing a date.
Not: answering "How long do I have to tell them I disagree?" or "When do I have to tell them?" with the statute's words alone.
Instead: for any question about when, how long, how many days, or a last day, call get_deadlines.

4. You propose facts; the tenant confirms them on the sheet.
Not: "Your confirmed dates: ..." or "Fact: claim_notice_date: 2026-09-22" before YOUR FACTS shows them as known.
Instead: call propose_facts with the tenant's exact words as "said" (shortened only by "..." between exact pieces); in the reply, say a point is not confirmed yet only where the answer turns on it.
Not: "Can you confirm the date you moved out?" or "Please tell me: your monthly rent, the new rent, and the date you got the notice."
Instead: read facts in YOUR FACTS; for anything the tenant states, call propose_facts; the sheet asks the tenant after your reply. Never ask in the chat to confirm or supply a fact listed in YOUR FACTS.

5. The open questions in a loaded skill's "What the statute does not settle" stay open, with their readings.
Not: "The termination date is the day you moved out." (an open question settled) or "Which date do you consider the termination of the rental agreement?" (asking the tenant to settle it)
Not: "The statute does not settle this." and nothing more.
Instead: "The statute does not settle this:" then the point in plain words, then each of the open question's readings and what it would mean on the tenant's facts. Never pick one. An open question with no readings is a limit of the tool: say what the tool does not compute.

[RULE 6]

7. Record each message the tenant pastes or describes with add_communication.
Not: a summary of the landlord's email as the text.
Instead: the text exactly as given; if its date is missing, ask for it first.
For a letter the tenant says they sent: sender "tenant", recipient "landlord", sent_on the date sent, channel the delivery method, and as text the draft's file name (draft_YYYY-MM-DD_issue_posture.txt, with the letter's date) then any tracking number. Ask for whatever is missing.

[RULE 8]

9. Offer nothing the tenant did not ask for.
Not: "Do you want to send a written objection to the landlord's claim?", "Would you like to proceed with any action based on this deadline?", "If you would like me to draft a letter..."
Instead: end with the last point of your answer. A step the statute requires before an option belongs in the answer; offering to draft it, or anything else, does not. Ask a question only when you need its answer for what the tenant asked.
"""

# Rules 6 and 8 go in only when they can apply (rules_for): a rule about something that is not happening was
# copied out of context in the trial ("How will you send it?" with no letter asked for, month-to-month story).
LETTER_RULE = """6. Letters only when the tenant asks, only through draft_letter.
Not: drafting, then asking the posture, then drafting again; or asking for days after the tenant wrote "Give them 5 days".
Not: "What exactly do you want the landlord to do?" after the tenant wrote "asking for my $900 back".
Instead: before draft_letter, ask once for whatever is missing: which issue (if more than one), what they want the landlord to do, days to reply, how they will send it (quote the notices clause), and the posture.
Not: "Preserve is the gentle option." or the posture lines retold without quote marks.
Not: LOADED SKILLS, deposit_not_returned, Letters: "preserve: States move-out date, ..." (labels from this prompt)
Instead: each posture line word for word after its name only, as preserve: "[its line]", then ask which; for assert or escalate, name the sentence the letter will quote.
Not: only "The letter appears above; tell me if you want changes." after "can you add the doctor's note? also does this letter count as my notice?"
Instead: after draft_letter, answer anything else the tenant asked in that message, as any answer, then end with "The letter appears above; tell me if you want changes." Never retell the letter. Changes go through draft_letter again; never write or rewrite a letter yourself."""

CASE_RULE = """8. Cases only through get_cases. The program prints them for the tenant, and you get their words to apply.
Not: "In Durene v. Alcime the court held a late notice forfeits the deposit, so your landlord forfeited yours." (a case named from memory, with no page, before get_cases printed it)
Not: "This tool has no cases on that." to "Has a court ever said anything about a notice that says cash only?" while COURT CASES THIS TOOL HAS lists "Three-day notice for nonpayment of rent".
Instead: when the tenant asks what courts or judges said, or a topic in COURT CASES THIS TOOL HAS is on the point you are applying (the same notice, deposit, repair, entry, rent, fee, or lease term), call get_cases with the topic's exact name from there, even if the topic does not name the tenant's exact point. Then, for every case it gives, not only those that help:
- its facts beside the tenant's: where they match and where they differ;
- its rule in one plain sentence with the case name and page, the court's own words in quote marks only where the point turns on them, and the statute version it read when that is not today's text;
- what the rule would mean on the tenant's facts, and whether another case distinguished it.
Say plainly when a case cuts against the tenant. Quote a case only from get_cases' result, and never say a case held anything its printed words do not.
Only when no topic is on the same thing, write exactly "This tool has no cases on that." and nothing after "that"."""

NO_CASES_RULE = """8. This tool has no cases for these issues. Never name a case from memory. Asked what courts or cases say, write exactly "This tool has no cases on that." and nothing after "that"."""

# Rule 6 joins once a letter is in play: the tenant's words in this chat mention a letter or writing one, or a
# letter was already drafted for this matter.
LETTER_WORDS = re.compile(r"\b(letters?|draft|write|writing)\b", re.I)


def rules_for(messages):
    """RULES with rule 6 (letters) only once a letter is in play, and rule 8 (cases) in full only when there
    is a case topic (one line saying there are none otherwise). A RULES_FILE without the markers is used
    as is."""
    letters = (any(m.type == "human" and LETTER_WORDS.search(str(m.content)) for m in messages)
               or any(ev["kind"] == "draft" for ev in read_events()))
    return (RULES.replace("[RULE 6]\n\n", LETTER_RULE + "\n\n" if letters else "")
                 .replace("[RULE 8]", CASE_RULE if offered_topics() else NO_CASES_RULE))


# RULES_FILE in the environment swaps in another rules text for one run, for trying versions of the rules,
# e.g. RULES_FILE=/path/rules_b.txt python dev/live_run.py ... The text above stays the default.
if os.environ.get("RULES_FILE"):
    RULES = Path(os.environ["RULES_FILE"]).read_text()


# ---- The System Prompt: built from whatever the record holds at the moment the model is called, on every call,
# so facts confirmed on the sheet and skills loaded mid-chat reach the model at once.

# The prompt's parts, in order, each under a name a tenant can read. The model names its sources, and with
# names like "ELEMENT STATUS" and "PLAYBOOKS" it wrote "(ELEMENT STATUS shows ...)" in 17 replies per 100, though
# the rules forbade it (TODO item 61). Under these names, a source named in plain words reads right to the tenant.
PARTS = {
    "lease": ("YOUR LEASE (only the clauses the tool reads from the tenant's lease, not the whole lease: each in plain "
              "words, with the cite to use and its words; search_lease searches the whole lease's text)"),
    "skills": ("SKILLS (every skill this tool has, with what it covers; load each one that fits the tenant's situation "
               "with load_skill)"),
    "loaded": "LOADED SKILLS (the instructions of each skill loaded for this matter, under its name: follow them)",
    "statute": "THE STATUTE (the sections the loaded skills list, Fla. Stat. ch. 83, part II)",
    "cases": "COURT CASES THIS TOOL HAS (topics for get_cases; number of cases on each)",
    "facts": "YOUR FACTS (by issue: known, changed, proposed, missing, or n/a, and where each came from)",
    "options": ("YOUR OPTIONS (checked by the program from the confirmed facts, the program's deadlines, and the lease "
                "clauses the tool has read: whether each option is open, closed, not known yet, not settled, outside the "
                "tool, or not open yet; each condition that decides it, with what the tool knows of it and, while it is "
                "not decided, what the option would be were it met; and how far its steps have got)"),
    # TODO item 83: each point an option turns on that the tool has not decided, gathered from YOUR OPTIONS once, with
    # what it would change; the model had stated such gaps as facts ("the lease does not mention any late fee").
    "unknown": ("WHAT THE TOOL DOES NOT KNOW (worked out by the program: each point an option turns on that the tool has "
                "not decided from the confirmed facts, a lease clause it read, or the statute; whether the tenant can "
                "tell the tool, can check it, it is not settled, it is outside the tool, or it is not yet; and what "
                "each would change)"),
    # Was THE PROGRAM'S DEADLINES (item 61, 2026-10-03), until the eval the same day: read as the deadlines
    # themselves, it was answered from ("You have until the upcoming deadline shown in THE PROGRAM'S DEADLINES")
    # and get_deadlines went uncalled on 5 of 39 questions about when.
    "deadlines": ("WHICH DEADLINES HAVE PASSED (passed or upcoming, no dates: for any question about when, call "
                  "get_deadlines, which prints the dates)"),
}


def system_prompt(messages=()):
    """The rules (rules_for the chat so far, `messages`), then each part under its name in PARTS: the lease profile,
    the menu of every skill (the loaded ones marked), each loaded skill's instructions under its name, the statute
    sections the loaded skills list, the case topics, the element status, the options (options_status), what the tool
    does not know (unknowns_status), and the deadline status (deadline_status: passed or upcoming, no dates), as the
    record stands now."""
    loaded = record.active_skills()
    menu = "\n".join(f"- {name}: {skill.description}" + (" (loaded)" if name in record.matter["skills"] else "")
                     for name, skill in skills.items())
    instructions = "\n\n".join(f"# {skill.name}\n{skill.body}" for skill in loaded) or "none loaded yet"
    sections = sorted({s for skill in loaded for s in skill.sections})
    hot = "\n\n".join(f"=== {s} ===\n{statute[s]}" for s in sections)
    return (rules_for(messages)
            + f"\n\n{PARTS['lease']}:\n" + lease_lines(record.profile)
            + f"\n\n{PARTS['skills']}:\n" + menu
            + f"\n\n{PARTS['loaded']}:\n" + instructions
            + f"\n\n{PARTS['statute']}:\n" + hot
            + f"\n\n{PARTS['cases']}:\n" + case_topics_text()
            + f"\n\n{PARTS['facts']}:\n" + json.dumps(element_status(), indent=2)
            + f"\n\n{PARTS['options']}:\n" + options_status()
            + f"\n\n{PARTS['unknown']}:\n" + unknowns_status()
            + f"\n\n{PARTS['deadlines']}:\n" + deadline_status())


def case_topics_text():
    """One line per case topic offered for the loaded skills, or a line saying there are none."""
    topics = offered_topics()
    return "\n".join(f"- {t} ({n})" for t, n in topics.items()) or "none for these issues"


# ---- The prompt's parts that the program works out: which deadlines have passed, the options, and what the tool does
# not know. Each logs nothing, since the prompt is rebuilt on every model call.

def deadline_status():
    """WHICH DEADLINES HAVE PASSED, for the system prompt (PARTS): each deadline of the ready issues, whose it is, what it counts
    from, its cite, and whether it has passed, with no date in it, then the issues still waiting and what for.
    So the model can apply a condition such as "within the 30-day period" from the program's "passed" or
    "upcoming", never from dates of its own (TODO item 46). Logs nothing: the prompt is rebuilt on every call."""
    waiting = open_facts_by_issue()
    ready = [pb for pb in active_playbooks() if pb.issue not in waiting]
    words = lambda ident: ident.replace("_", " ")         # labels, not ids: the model copies an id it reads (item 53)
    lines = []
    for d in matter_deadlines(ready, record.matter["facts"], date.today()):
        issues = ", ".join(words(i) for i in d["issues"])
        if "deadline" not in d:
            lines.append(f"- {words(d['clock'])} [{issues}]: no date ({words(d['status'])})")
            continue
        start = d["from"].split()[0]                       # the trigger; its date stays out
        lines.append(f"- {words(d['clock'])} [{issues}]: the {d['actor']}'s, {d['rule']} {words(start)}, Fla. Stat. "
                     f"{d['cite']}: {d['status']}" + (f" (counts only if {d['condition']})" if "condition" in d else ""))
    lines += [f"- waiting [{words(issue)}]: no deadline until these are confirmed: {', '.join(words(i) for i in ids)}"
              for issue, ids in waiting.items()]
    return "\n".join(lines) or "none: no active issue has a deadline this tool computes"


def state_words(x):
    """A gate's or a way's state in words: its status, then what the tool knows of it when that says more (the tenant
    can tell the tool, the tenant can check), then why."""
    words = x["status"]
    if x["knowledge"] not in ("known", x["status"]):
        words += f", {x['knowledge']}"
    return words + (f": {x['why']}" if "why" in x else "")


def options_status():
    """YOUR OPTIONS, for the system prompt (PARTS): for each active issue's options
    (deterministic.check_options, from the confirmed facts and the lease profile), the option, its cite, and its
    status; then each condition that decides it with its state in words (state_words): met, not met, not met yet,
    or not known yet because the tenant can tell the tool or can check, not settled, or outside the tool, and why;
    for a condition not met that has several ways to be met, each way with its own state; for one not yet decided,
    what the option would be were it met, unless another condition closes it anyway (were it not, the option is
    closed; TODO item 81); each step and whether it
    is done, waiting, or to do; and the open questions that bear on it even so, by their first sentence. In words,
    never an id (TODO item 53). Logs nothing: the prompt is rebuilt on every call."""
    facts = record.matter["facts"]
    lines = []
    for pb in active_playbooks():
        first_sentence = {q["id"]: " ".join(q["text"].split()).split(". ")[0] + "."
                          for q in pb.spec.open_questions if isinstance(q, dict)}
        for o in check_options(pb, facts, date.today(), record.profile):
            lines.append(f"- {o['label']} (Fla. Stat. {o['cite']}): {o['status'].upper()}")
            for g in o["gates"]:
                ways = [w for w in g["ways"] if w.get("why") != NOT_APPLY] or g["ways"]    # a way for another case: out
                several = len(ways) > 1 and g["state"] != "met"
                lines.append(f"    condition: {g['says']} ({g['cite']}): "
                             + (f"{g['status']}, met through any of these:" if several else state_words(g)))
                if several:
                    lines += [f"      - {w['says']} ({w['cite']}): {state_words(w)}" for w in ways]
                if g["state"] not in ("met", "not met") and g["if_met"] != "closed":   # else another closes it
                    lines.append(f"      if this condition is met, the option is {g['if_met']}; if it is not, the "
                                 "option is closed")
            for s in o["steps"]:
                lines.append(f"    step: {s['says']} ({s['cite']}): {s['status']}" + (f": {s['why']}" if "why" in s else ""))
            for q in o["also_open"]:
                lines.append(f"    also, from what the statute does not settle: {first_sentence.get(q, '')}")
    return "\n".join(lines) or "none: no active issue lists its options yet"


# What the answer depends on that the tool does not know (TODO item 83, the author's decision of 2026-10-04): every
# point an option turns on that is not settled from the confirmed facts, a lease clause the tool read, or the statute,
# once, with what the tool knows of it and what it would change. In the eval of 2026-10-04 the model stated such gaps
# as facts ("the lease does not mention any late fee") or left them out of the answer.
UNDECIDED = ("tell", "check", "not settled", "outside", "not met yet")
KNOWN_AS = {"tell": "the tenant can tell the tool", "check": "the tenant can check", "not settled": "not settled",
            "outside": "outside the tool", "not met yet": "not yet"}


def unknowns_status():
    """WHAT THE TOOL DOES NOT KNOW, for the system prompt (PARTS): each point an option of an active issue turns
    on that the tool has not decided (deterministic.check_options: a way of a gate not decided, UNDECIDED) and that
    could change an option (one another condition closes is left out), once, in words: what it is, with its cite and issue; what the tool knows of it (the tenant can tell the tool, the tenant can
    check, not settled, outside the tool, not yet) and why; then, for each option it decides, what the option would be
    if it holds, and what is left if it does not (the condition's other undecided ways, or the option closed). Then
    the lease: the parts the tool has not read, and that search_lease searches the rest. Logs nothing."""
    points = {}
    for pb in active_playbooks():
        for o in check_options(pb, record.matter["facts"], date.today(), record.profile):
            for g in o["gates"]:
                if g["state"] not in UNDECIDED or g["if_met"] == "closed":   # decided, or another condition closes it
                    continue
                undecided = [w for w in g["ways"] if w["state"] in UNDECIDED]
                for w in undecided:
                    point = points.setdefault((w["says"], w["cite"], w.get("why", "")), {"issues": [], "effects": [], **w})
                    if pb.issue.replace("_", " ") not in point["issues"]:
                        point["issues"].append(pb.issue.replace("_", " "))
                    others = [x["says"] for x in undecided if x is not w]
                    point["effects"].append(f"{o['label']}: {g['if_met']} if it holds; if not, "
                                            + (f"the condition turns on whether {' or whether '.join(others)}" if others
                                               else "closed"))
    lines = []
    for (says, cite, why), point in points.items():
        lines.append(f"- whether {says} ({cite}) [{', '.join(point['issues'])}]: {KNOWN_AS[point['state']]}"
                     + (f": {why}" if why else ""))
        lines += [f"    {effect}" for effect in point["effects"]]
    if record.profile is not None:
        unread = [LABELS[name] for name in type(record.profile).model_fields if getattr(record.profile, name) is None]
        if unread:
            lines.append(f"- the parts of the lease on {', '.join(unread)}: not read from this lease")
    lines.append("- anything else in the lease: YOUR LEASE holds only the clauses the tool reads; search_lease searches the "
                 "whole text, and only a point no wording finds there is known to be absent")
    return "\n".join(lines)
