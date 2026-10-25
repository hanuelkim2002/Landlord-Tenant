"""The six tools the model can call, each a short function, and their descriptions as the model sees them.
count_days is the only date math for deadlines.
"""
from datetime import date, timedelta

import law
import record

COUNTING = ("Counted in calendar days, the start day not counted, with no weekend or holiday shift; this way of "
            "counting has not been checked against the statute yet.")


def get_statute_section(m, section):
    """The full text of one stored section of ch. 83, part II."""
    text = law.section_text(str(section))
    return text or f"No section {section} in the stored statute. The stored sections: {', '.join(law.section_titles())}."


def search_statute(m, phrase):
    """Every stored section that holds a phrase, with the words around it."""
    found = law.search_statute(str(phrase))
    if not found:
        return f"No stored section holds \"{phrase}\". Try other words."
    return "\n\n".join(f"{section}: ...{words}..." for section, words in found[:8])


def load_skill(m, name):
    """Load a skill for this matter: its instructions stay in the prompt from now on."""
    skill = law.skills().get(str(name))
    if not skill:
        return f"No skill named {name}. The skills: {', '.join(law.skills())}."
    record.add_skill(m, skill["name"])
    return f"Loaded {skill['name']}. Its instructions:\n\n{skill['body']}"


def count_days(m, fact, days):
    """A confirmed date plus some days (negative for before it), and whether that date has passed today."""
    value = record.confirmed_facts(m).get(str(fact))
    if value is None:
        return f"{fact} is not a confirmed fact yet, so nothing can be counted from it. The tenant confirms facts in the sidebar."
    try:
        start, days = date.fromisoformat(value), int(days)
    except ValueError:
        return f"{fact} is confirmed as {value!r}, which is not a date written YYYY-MM-DD."
    due, today = start + timedelta(days=days), date.today()
    status = "has passed" if due < today else "is today" if due == today else "has not passed"
    return f"{fact} ({start}) {'+' if days >= 0 else '-'} {abs(days)} days = {due}, which {status} (today is {today}). {COUNTING}"


def note_fact(m, name, value, tenant_words):
    """Save what the tenant said as a pending fact, for them to confirm in the sidebar."""
    try:
        record.note_fact(m, str(name), str(value), str(tenant_words))
    except ValueError as problem:
        return str(problem)
    return f"Noted {name} = {value} as pending. It counts only once the tenant confirms it in the sidebar."


def today():
    """Today's date. A helper, because save_line's parameter named date hides the date class inside it."""
    return date.today()


def save_line(m, number, date, what, open):
    """Save one line of the timeline. "today" as the date is turned into today's date here, by code."""
    date = str(today()) if str(date).strip().lower() == "today" else str(date).strip()
    open = str(open).lower() == "true"                       # a model may send the word instead of true or false
    try:
        number = record.save_line(m, int(number), date, str(what), open)
    except ValueError as problem:
        return str(problem)
    return f"Saved line {number}: {date or 'no date'}: {what}" + (" (open)." if open else ".")


RUN = {"get_statute_section": get_statute_section, "search_statute": search_statute, "load_skill": load_skill,
       "count_days": count_days, "note_fact": note_fact, "save_line": save_line}


def tool(tool_name, about, **parameters):
    """One tool's description in the form the gateway expects; every parameter is required."""
    return {"type": "function", "function": {"name": tool_name, "description": about, "parameters": {
        "type": "object", "properties": parameters, "required": list(parameters)}}}


TEXT, NUMBER, BOOLEAN = {"type": "string"}, {"type": "integer"}, {"type": "boolean"}
SCHEMAS = [
    tool("get_statute_section", "Read the full text of one section of Fla. Stat. ch. 83, part II, like 83.49.",
         section=TEXT),
    tool("search_statute", "Find the sections of ch. 83, part II that hold a phrase, with the words around it.",
         phrase=TEXT),
    tool("load_skill", "Load the skill whose description fits the tenant's situation, by its name in SKILLS. Its "
         "instructions come back now and stay in your instructions for this matter.", name=TEXT),
    tool("count_days", "The only way to work with dates. Takes the name of a confirmed fact holding a date and a "
         "number of days (negative for a deadline before that date); returns the date and whether it has passed.",
         fact=TEXT, days=NUMBER),
    tool("note_fact", "Save a fact the tenant told you, as pending, for the tenant to confirm. name: lowercase words "
         "joined by underscores, like lease_end_date. value: a date as YYYY-MM-DD, otherwise plain words. "
         "tenant_words: what the tenant said, in their words.", name=TEXT, value=TEXT, tenant_words=TEXT),
    tool("save_line", "Save one line of the timeline: one thing that happened between the people in the dispute, or "
         "to the home (a message, a visit, a payment, a promise, a repair, a move). number: 0 for a new line, or a "
         "line's number to save a new version of it, to fix it or close it. date: YYYY-MM-DD if the tenant gave the "
         "exact day, \"today\" if it happened today, otherwise the tenant's words (like \"last Monday\"), or empty. "
         "what: plain words, with who did it and how. open: true while something is still waiting on this line.",
         number=NUMBER, date=TEXT, what=TEXT, open=BOOLEAN),
]


def run_tool(m, name, arguments):
    """Run one tool call for this matter; a call with a wrong name or missing arguments gets a plain reply."""
    if name not in RUN:
        return f"No tool named {name}."
    try:
        return RUN[name](m, **arguments)
    except TypeError:
        return f"{name} needs: {', '.join(next(s for s in SCHEMAS if s['function']['name'] == name)['function']['parameters']['required'])}."
