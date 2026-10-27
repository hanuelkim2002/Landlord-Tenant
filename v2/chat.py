"""The chat: the system prompt (the rules, the whole lease, the facts, the timeline, the skills) and the tool loop,
which sends the messages, runs any tool calls, sends the results back, and repeats until the model answers. Also the
split of a reply into the short answer the page shows first and the points it shows behind a click.
"""
import json
import re

import checks
import config
import law
import lease
import record
import tools

MAX_ROUNDS = 8                                               # tool rounds before the model is asked to answer

RULES = """You help a tenant in Florida with a dispute with their landlord, under Fla. Stat. ch. 83, part II.

1. Apply the law to the tenant's facts and give an answer, not a list of quotes.
2. Answer what was asked first. When asked "can I ...", say whether they can before giving any step.
3. Know what you know. Each point the answer turns on is one of these: known (a confirmed fact, a lease clause you read, the statute), something the tenant can tell you, something they must check, unsettled, or outside the tool. Never state a gap as a fact, and never assume a fact you haven't been given. Say how an unknown would change the answer.
4. An open question stays open: give the reading on each side.
5. Ask the tenant only plain facts (what happened, when, how something was sent, what a paper says). Never ask whether something meets a legal term.
6. Cite each rule to its source: a statute section and subsection, or the lease. Put in quotation marks only the statute's or the lease's own words. Say everything else in your own words: what the tenant told you, the facts they confirmed, and any message, letter, or paper they describe.
7. Dates come only from count_days. Never add, subtract, or compare dates yourself.
8. End with the one question your answer needs, if any. Don't offer help the tenant didn't ask for, and never repeat an offer.
9. Keep the timeline with save_line: one line for each thing that happens between the tenant and the landlord, or to the home. A line is open only while it waits for one specific next thing, like a reply, a visit, a repair, or a payment; it is not open just because the dispute goes on. When the tenant reports that thing, or it can no longer happen, close the line that was waiting for it: save it again with its number and open false. To fix a line, save it again with its number. A date a skill counts from is also noted as a fact.
10. When there is a SINCE LAST VISIT block, the tenant is back after a gap. Start from what they say and the open lines; if an open line is still unsettled, ask about it once. Never ask again for what the facts, the timeline, or the chat already hold.

Reading the lease:
1. THE LEASE below is the tenant's whole lease, page by page. Read all of it, addenda and tables included, before you say whether it covers a point.
2. Say the lease does not address a point only if no part of it does. If a clause comes close but does not settle the point, say what it does say.
3. Quote the lease's own words, and cite the section number, or the page when there is none.
4. A choice in the lease counts only if it is marked: a checked box, or initials on the line. An unchecked box or a blank initials line was not chosen.

Looking things up: when you need several lookups (statute sections, skills, day counts, facts to note), ask for all of them in the same step, not one at a time."""


def facts_text(facts, pending=False):
    """Facts for the prompt, one a line, with the tenant's words for a pending one."""
    lines = [f"- {name}: {f['value']}" + (f" (the tenant said: {f['tenant_words']})" if pending else "")
             for name, f in facts.items()]
    return "\n".join(lines) or "- none yet"


def timeline_text(lines):
    """The timeline for the prompt, one line each, oldest first, the open ones marked."""
    shown = [f"- {number}. {line['date'] or '(no date)'}: {line['what']}" + (" (open)" if line["open"] else "")
             for number, line in lines.items()]
    return "\n".join(shown) or "- none yet"


def since_text(since):
    """The since-last-visit block for the prompt, or nothing when the tenant has not been away a day."""
    if since is None:
        return ""
    days = f"{since['days']} day" + ("" if since["days"] == 1 else "s")
    text = f"\n\nSINCE LAST VISIT (counted by code):\nThe last message was {days} ago."
    if since["changed"]:
        text += " Since then the tenant confirmed:"
        for c in since["changed"]:
            corrected = f" (first noted as {c['noted_value']})" if c["value"] != c["noted_value"] else ""
            text += f"\n- {c['fact']}: {c['value']}{corrected}"
    return text


def system_prompt(m, pages):
    """Everything the model is told for this matter, built fresh for each message."""
    all_skills = law.skills()
    listed = "\n".join(f"- {s['name']}: {s['description']}" for s in all_skills.values())
    loaded = "\n\n".join(f"## {name}\n{all_skills[name]['body']}" for name in m["skills"] if name in all_skills)
    return (f"{RULES}\n\nTHE LEASE (the tenant's whole lease):\n{lease.lease_text(pages) or 'No lease uploaded.'}\n\n"
            f"CONFIRMED FACTS (the tenant confirmed these; only these count):\n{facts_text(m['confirmed'])}\n\n"
            f"PENDING FACTS (noted with note_fact, not yet confirmed by the tenant; they do not count yet):\n"
            f"{facts_text(m['pending'], pending=True)}\n\n"
            f"TIMELINE (what happened, oldest first; keep it with save_line):\n{timeline_text(m['lines'])}"
            f"{since_text(record.since_last_visit(m))}\n\n"
            f"SKILLS (load each one that fits the tenant's situation with load_skill):\n{listed}\n\n"
            f"LOADED SKILLS:\n{loaded or 'none yet'}")


DETAILS = "DETAILS"                                          # the line between the short answer and the points
WHY = "Why, and the law behind it"                           # the title for reasons written before any heading
# The marker line holds only DETAILS, in any case, maybe bold or with a colon. Spaces and tabs only, never a newline,
# so the match stays on one line.
MARKER = re.compile(rf"(?im)^[ \t]*\**[ \t]*{DETAILS}[ \t]*:?[ \t]*\**[ \t]*$")
HEADING = re.compile(r"(?m)^#+[ \t]+(.*)$")


def split_reply(text):
    """A reply's short part, shown first, and its points as [(title, body)], each shown behind a click."""
    marker = MARKER.search(text)
    if not marker:
        return text.strip(), []                              # an old reply, or no marker: show it whole
    details = text[marker.end():]
    headings = list(HEADING.finditer(details))
    points = [(WHY, details[:headings[0].start()] if headings else details)]
    for heading, following in zip(headings, headings[1:] + [None]):
        points.append((heading.group(1).strip("* \t"), details[heading.end():following.start() if following else None]))
    return text[:marker.start()].strip(), [(title, body.strip()) for title, body in points if body.strip()]


TEXT_CALL = re.compile(r"<function=([\w-]+)>(.*?)</function>", re.S)
TEXT_PARAMETER = re.compile(r"<parameter=([\w-]+)>\s*(.*?)\s*</parameter>", re.S)


def text_tool_calls(content):
    """Tool calls the model wrote out as text instead of making them, as [(name, arguments)]. Nemotron does this
    now and then; without running them, the tenant would see the call as the reply."""
    calls = []
    for name, inner in TEXT_CALL.findall(content or ""):
        arguments = {}
        for key, value in TEXT_PARAMETER.findall(inner):
            try:
                arguments[key] = json.loads(value)
            except json.JSONDecodeError:
                arguments[key] = value
        calls.append((name, arguments))
    return calls


def run_loop(m, messages):
    """Send the messages, run every tool call, send the results back, and repeat until the model answers."""
    gateway = config.client()
    for round_number in range(MAX_ROUNDS + 1):
        request = {"model": config.AGENT_MODEL, "messages": messages, **config.temperature(config.GATEWAY), "max_tokens": 8000,
                   "tools": tools.SCHEMAS}
        if round_number == MAX_ROUNDS:
            request["tool_choice"] = "none"                  # out of rounds: answer from what was read
        message = gateway.chat.completions.create(**request).choices[0].message
        content = message.content or ""
        if message.tool_calls:
            messages.append({"role": "assistant", "content": content,
                             "tool_calls": [c.model_dump() for c in message.tool_calls]})
            for call in message.tool_calls:
                try:
                    arguments = json.loads(call.function.arguments or "{}")
                except json.JSONDecodeError:
                    arguments = {}
                messages.append({"role": "tool", "tool_call_id": call.id,
                                 "content": tools.run_tool(m, call.function.name, arguments)})
        elif text_tool_calls(content) and round_number < MAX_ROUNDS:
            messages.append({"role": "assistant", "content": content})
            for name, arguments in text_tool_calls(content):
                messages.append({"role": "user", "content": f"Result of {name}:\n{tools.run_tool(m, name, arguments)}"})
        else:
            return re.sub(r"<think>.*?</think>", "", content, flags=re.S).strip()
    return ""


def reply(m, text):
    """Answer the tenant's message: record it, run the chat, check the reply, record it. Returns (reply, checks)."""
    pages = lease.lease_pages(m)
    messages = [{"role": "system", "content": system_prompt(m, pages)}]
    messages += [{"role": c["role"], "content": c["text"]} for c in record.chat(m)]
    messages.append({"role": "user", "content": text})
    record.add_message(m, "user", text)
    answer = run_loop(m, messages)
    shown = checks.check_reply(answer, pages)
    record.add_message(m, "assistant", answer, shown)
    return answer, shown
