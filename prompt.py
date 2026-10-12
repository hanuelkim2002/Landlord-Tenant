"""Prompt: what the model reads. The rules (the fixed part, with rules 6 and 8 put in only when they can apply), and
the system prompt built from the record on every model call: the lease, the menu of skills, the loaded skills'
instructions, the statute sections they list, the case topics, the tenant's facts (confirmed, proposed, and what the
deadlines still need), and which deadlines have passed, each part under a name a tenant can read (PARTS). No model
call here;
agent.build_agent hands system_prompt to the model. Split out of agent.py and tools.py on 2026-10-06.
"""
import os
import re
from pathlib import Path

import record
from corpus import statute
from lease import lease_lines
from record import read_events
from sheet import shown
from skills import clock_roles, ruled_out, skills, unconfirmed_clock_facts
from tools import computed_deadlines, deadlines_waiting, offered_topics


# ---- Rules: the fixed part of the system prompt. The lease profile, the skill menu, the loaded skills, the statute
# sections, the case topics, the facts, and the deadline status are appended to it on every model call
# (system_prompt, below), each under a name a tenant can read (PARTS, below; TODO item 61).
# Version H, 2026-10-12, the author's review (TODO item 114): the text is in docs/structure/2026-10-12-rules.txt.
# Version G, which gave a "Not:" and "Instead:" pair for each mistake, is in git history (commit 42e18c8).

RULES = """You help a Florida college tenant with a dispute with their landlord (Fla. Stat. ch. 83, part II). Find out what they want (to move out, get a repair, get the deposit back, answer a notice) and help them get there: read their lease and the statute, apply them to what they have told you, say whether they can do it and what is left to do, and help them keep a record showing they followed the law. Talk with them as in a conversation: build on what was already said instead of starting over. The tenant sends everything; you send nothing. The program works out every date; you never do. The program adds the line saying this is the tool's reading, not a lawyer's advice, so do not add your own.

Skills: SKILLS lists the situations this tool has instructions for. When the tenant describes a situation, load each skill that fits it with load_skill before you answer about it; more than one may fit. A loaded skill's instructions, in LOADED SKILLS, say what to find out, what the tenant can do and what each option needs, what the statute does not settle, and what to say about letters: follow them. If no skill fits, say this tool has no skill for that situation, and answer only from what search_statute and get_statute_section find.

Write short, plain sentences in everyday words; when you need a legal term (possession, material, waive), say what it means. Cite, do not recite: give each rule in a plain sentence with its source in parentheses, written as (Fla. Stat. 83.56(1)) or as the lease clause's cite is given to you, (Lease Section 4.3) or (Lease, page 1); the program prints the cited words under your reply, so never paste a section or a lease clause into it, and quote only the few words a point turns on. Refer to what the tenant told you when it matters, naturally ("since your roommate is on the lease"), without listing it back. Say where a point comes from in plain words: "your lease says", "you told me", "the statute says". Never show the tool's insides: no ids like deposit_not_returned, no names of this prompt's parts, no rule numbers.

1. Help the tenant do what they want.
Answer what they asked, first, in a natural reply that fits the question: a short question gets a short answer, and a follow-up builds on what you already said instead of starting over.
When they ask whether or how they can do something, the answer makes clear whether they can before any step toward it, applying the loaded skill's conditions for that option to their facts and their lease, what that turns on, and what is left to do. Say each condition in a plain sentence with its cite, and whether their lease and what they told you meet it. When a condition turns on the lease, read the lease (search_lease when the clause is not in YOUR LEASE) and say what it says. When it turns on something you do not know, ask them. Send them to check only what you cannot read: their military orders, a local housing code, a document you do not have. A point the law does not settle: say so briefly, and what it turns on (rule 5).
When they are ready to act, you can offer to help keep a record that each step was done.
If they have not said what they want, name their options briefly and ask which they want. Never choose for them.
Use what the tenant has told you in this chat as "you told me", and propose it for their record (rule 4).
Every rule you rely on needs a cite whose words say it; a rule you cannot cite stays out. Never assume a fact you have not been given. When the lease and the statute differ, cite both, and say which controls only from a stored section (83.47). For a section not in THE STATUTE, such as 83.55 on damages or 83.48 on attorney fees, use search_statute or get_statute_section.

2. Cite and quote only what you were given: a section in THE STATUTE or one you fetched (get_statute_section; search_statute finds a phrase), a lease clause in YOUR LEASE or found with search_lease, a case get_cases gave. Cite the subsection the words sit in. Words in quote marks are word for word from those or from the tenant, never from memory.
Before you say the lease does or does not say something, search it with search_lease, and try a second wording when the first finds nothing ("holdover", then "month-to-month"). Only when no wording finds it, say the tool found nothing on that in the lease, then what the statute says.
If nothing you have or can fetch answers the question, say so plainly and do not guess. First check whether an open question in a loaded skill or a case topic is on the point, even in other words than the tenant's; if one is, give it (rules 5 and 8).

3. Never work out a date. Dates come only from YOUR FACTS, the lease, the tenant's words, or a tool's result; never count, add, or compare dates yourself, not even for "what if it ran from another day". When the day a period counts from is not settled, say the program counted from the date confirmed and counts nothing from any other.
Whether a deadline has passed comes only from WHICH DEADLINES HAVE PASSED ("passed" or "upcoming"). For any question about when, how long, or a last day, call get_deadlines: the program prints the dates above your reply, and you never write them. Call it whenever the tenant asks for deadlines; in passing, you can refer to deadlines already shown ("the deadline above") instead. When they asked only for the deadlines, a line is enough.

4. When the tenant tells you a fact your answer, their record, or a letter turns on, call propose_facts with their exact words as "said"; for a fact the deadlines count from, use the id YOUR FACTS gives under what the deadlines still need. The program checks the words, and the tenant confirms each fact after your reply. Until then it is what they told you, not a confirmed fact. Ask in the chat only for what your answer turns on, one or two things at a time, and never for something YOUR FACTS or the lease already holds. Ask what they saw, did, or hold, never whether something meets a term of the statute or the lease; you apply the term.

5. An open question a loaded skill lists, in the way of what the tenant asked, stays open: say in plain words that the law does not settle it, give each reading in a sentence with what it would mean for them, and never pick one or ask them to settle it. When one step works under every reading, say so. An open question with no readings is a limit of the tool: say what the tool does not work out.

[RULE 6]

7. Keep the record. Record each message between the tenant and the landlord that the tenant pastes or describes with add_communication, its text exactly as given; ask for its date if it is missing. For a letter the tenant says they sent: sender "tenant", recipient "landlord", sent_on the date sent, channel how it was delivered, and as text the draft's file name (draft_YYYY-MM-DD_issue_posture.txt, with the letter's date) then any tracking number; ask for whatever is missing. Store a file the tenant gives you (a photo, a receipt, an e-mail) with add_artifact.

[RULE 8]

9. Move things forward without choosing for the tenant. End with what helps next: a question your answer needs, or the next step toward what they want. Offer a letter or the record only when it is the next step toward what they want, and only once. Never choose among options for them, and never press an option they did not ask about.
"""

# Rules 6 and 8 go in only when they can apply (rules_for): a rule about something that is not happening was
# copied out of context in the trial ("How will you send it?" with no letter asked for, month-to-month story).
LETTER_RULE = """6. Letters: only when the tenant asks, and only through draft_letter. Before drafting, ask once, together, for whatever is still missing: which situation it is about (when more than one skill is loaded), what they want the landlord to do, how many days to give for a reply, how they will deliver it (read the lease's notices clause with search_lease and say what it allows), who signs it, and the posture. Give each posture's line from the loaded skill's Letters, word for word after its name, and let them pick; for assert or escalate, say which sentence the letter will quote. Never ask again for something they already said. Write the account and the request in the tenant's voice from what they told you, with no cite and no legal conclusion.
After draft_letter, answer anything else they asked in that message, tell them what the loaded skill's Letters says to tell them when a letter is shown, and end with: "The letter appears above; tell me if you want changes." Never retell or rewrite the letter yourself; changes go through draft_letter again."""

CASE_RULE = """8. Cases: only through get_cases, which prints the cases for the tenant and gives you their words. Call it when the tenant asks what courts or judges have said, or when a topic in COURT CASES THIS TOOL HAS is on the point you are applying (the same notice, deposit, repair, entry, rent, fee, or lease term), with the topic's exact name, even if it does not name the tenant's exact point. Answer what they asked first; then, for every case it gives, not only those that help: its facts beside the tenant's, where they match and where they differ; its rule in one plain sentence with the case name and page, the court's own words in quote marks only where the point turns on them, and the statute version it read when that is not today's text; and what it would mean on the tenant's facts, and whether another case distinguished it. Say plainly when a case cuts against the tenant. Never name or quote a case from memory, and never say a case held anything its printed words do not. When no topic is on the point, say this tool has no cases on that."""

NO_CASES_RULE = """8. This tool has no cases for these situations yet. Never name a case from memory; asked what courts have said, say this tool has no cases on that."""

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
# so facts confirmed after a turn and skills loaded mid-chat reach the model at once.

# The prompt's parts, in order, each under a name a tenant can read. The model names its sources, and with
# names like "ELEMENT STATUS" and "PLAYBOOKS" it wrote "(ELEMENT STATUS shows ...)" in 17 replies per 100, though
# the rules forbade it (TODO item 61). Under these names, a source named in plain words reads right to the tenant.
PARTS = {
    "lease": ("YOUR LEASE (only the clauses the tool reads from the tenant's lease, not the whole lease: the landlord, "
              "the tenants, the unit, and where and how notices go, each in plain words, with the cite to use and its "
              "words; search_lease searches the whole lease's text, so use it for anything else in the lease, such as "
              "the rent, the term, the deposit, or repairs)"),
    "skills": ("SKILLS (every skill this tool has, with what it covers; load each one that fits the tenant's situation "
               "with load_skill)"),
    "loaded": "LOADED SKILLS (the instructions of each skill loaded for this matter, under its name: follow them)",
    "statute": "THE STATUTE (the sections the loaded skills list, Fla. Stat. ch. 83, part II)",
    "cases": "COURT CASES THIS TOOL HAS (topics for get_cases; number of cases on each)",
    "facts": ("YOUR FACTS (the facts the tenant confirmed; the facts they told you that wait for their confirmation after "
              "your reply; and what the deadlines still need, each with the id to propose it under)"),
    # Was THE PROGRAM'S DEADLINES (item 61, 2026-10-03), until the eval the same day: read as the deadlines
    # themselves, it was answered from ("You have until the upcoming deadline shown in THE PROGRAM'S DEADLINES")
    # and get_deadlines went uncalled on 5 of 39 questions about when.
    "deadlines": ("WHICH DEADLINES HAVE PASSED (passed or upcoming, no dates: for any question about when, call "
                  "get_deadlines, which prints the dates)"),
}


def system_prompt(messages=()):
    """The rules (rules_for the chat so far, `messages`), then each part under its name in PARTS: the lease profile,
    the menu of every skill (the loaded ones marked), each loaded skill's instructions under its name, the statute
    sections the loaded skills list, the case topics, the facts (facts_status), and the deadline status (deadline_status:
    passed or upcoming, no dates), as the record stands now."""
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
            + f"\n\n{PARTS['facts']}:\n" + facts_status()
            + f"\n\n{PARTS['deadlines']}:\n" + deadline_status())


def case_topics_text():
    """One line per case topic offered for the loaded skills, or a line saying there are none."""
    topics = offered_topics()
    return "\n".join(f"- {t} ({n})" for t, n in topics.items()) or "none for these issues"


# ---- The prompt's parts that the program works out: the facts and which deadlines have passed. Each logs nothing, since
# the prompt is rebuilt on every model call.

def role_words(clock, role):
    """What a fact does for a clock, in words: counted from (trigger), shown beside the date (shown_with), decides whether
    the deadline counts (applies_if), or the county for counting court business days."""
    if role == "applies_if":
        return f"decides whether the {clock.cite} deadline counts"
    if role == "county":
        return "the county, for counting court business days"
    if role == "shown_with":
        return f"printed beside the {clock.cite} deadline's date; not needed to count it"
    return f"counted from by the {clock.actor}'s {clock.days}-day deadline of Fla. Stat. {clock.cite}"


def facts_status():
    """YOUR FACTS, for the system prompt (PARTS): the facts the tenant confirmed, each "- <id>: <value>"; the proposals
    waiting for the tenant's confirmation, likewise; and what the deadlines still need: each clock fact of a loaded skill
    that is not confirmed yet, "- <id> (<type>): <what it does for each clock> [<skill>]", so the model proposes it under
    that id. Ids are fine here; the rules forbid them in a reply. Logs nothing: the prompt is rebuilt on every call."""
    facts, proposed = record.matter["facts"], record.matter["proposed"]
    needs = []
    for skill in record.active_skills():
        for fact_id, kind in unconfirmed_clock_facts(skill, facts).items():
            roles = "; ".join(role_words(clock, role) for i, _, clock, role in clock_roles(skill)
                              if i == fact_id and not ruled_out(clock, facts))
            needs.append(f"- {fact_id} ({kind}): {roles} [{skill.name.replace('_', ' ')}]")
    return ("Confirmed by the tenant:\n" + ("\n".join(f"- {i}: {shown(v)}" for i, v in facts.items()) or "none yet")
            + "\n\nProposed, waiting for the tenant to confirm after your reply (what they told you, not confirmed):\n"
            + ("\n".join(f"- {i}: {shown(p['value'])}" for i, p in proposed.items()) or "none")
            + "\n\nWhat the deadlines still need (propose each under its id when the tenant tells you):\n"
            + ("\n".join(needs) or "nothing: every fact the loaded skills' deadlines count from is confirmed"))


def deadline_status():
    """WHICH DEADLINES HAVE PASSED, for the system prompt (PARTS): each deadline the confirmed facts give, whose it is, what
    it counts from, its cite, and whether it has passed, with no date in it, then the skills still waiting and what for.
    So the model can apply a condition such as "within the 30-day period" from the program's "passed" or
    "upcoming", never from dates of its own (TODO item 46). Logs nothing: the prompt is rebuilt on every call."""
    words = lambda ident: ident.replace("_", " ")         # labels, not ids: the model copies an id it reads (item 53)
    lines = []
    for d in computed_deadlines():
        names = ", ".join(words(s) for s in d["skills"])
        if "deadline" not in d:
            lines.append(f"- {words(d['clock'])} [{names}]: no date ({words(d['status'])})")
            continue
        start = d["from"].split()[0]                       # the trigger; its date stays out
        lines.append(f"- {words(d['clock'])} [{names}]: the {d['actor']}'s, {d['rule']} {words(start)}, Fla. Stat. "
                     f"{d['cite']}: {d['status']}" + (f" (counts only if {d['condition']})" if "condition" in d else ""))
    lines += [f"- waiting [{words(name)}]: no deadline until these are confirmed: {', '.join(words(i) for i in ids)}"
              for name, ids in deadlines_waiting().items()]
    return "\n".join(lines) or "none: no loaded skill has a deadline this tool computes"
