"""Helpers shared by the smoke parts: a phrase of 83.49(3)(a) the quote checks use, and small helpers for the
checks that write to a matter. (Named checks and scratch matters are in checks.py.)"""
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel

import record
from prompt import PARTS, system_prompt
from visit import Visit

FORFEIT = "he or she forfeits the right to impose a claim upon the security deposit"     # in 83.49(3)(a)


def visit_here(replied=True):
    """A Visit on the matter and session open in the record, with no agent, for the checks of the confirmation that
    must not call the model. replied=True: the model already replied to a confirmation of this tenant message, so
    Visit.confirm saves the answers and carries the note, with no automatic reply."""
    visit = Visit(record.matter["tenant"], record.matter["id"])
    visit.session_id = record.session
    visit.replied = replied
    return visit


def confirm_rows(visit, answers):
    """Answer the visit's confirmation the way the web page does, one row at a time: each answer goes to the first row
    still open; an answer that is refused leaves its row open, so the next answer goes to that row again. Fails
    loudly if the answers run out. Returns every block the calls returned and what each refusal expected."""
    answers = iter(answers)
    rows, blocks, refused = visit.rows(), [], []
    while rows:
        result = visit.confirm({rows[0]["id"]: next(answers)})
        blocks += result.blocks
        refused += result.refused.values()
        rows = result.rows
    return blocks, refused


def stated(value, words):
    return {"value": value, "how": "stated", "basis": words}


def screen(blocks):
    """The blocks' texts as one string, to look for what the tenant would read."""
    return "\n".join(b["text"] for b in blocks)


def prompt_part(key):
    """One part of the system prompt as it stands now (prompt.PARTS), without its name."""
    after = system_prompt().split("\n\n" + PARTS[key] + ":\n")[1]
    later = list(PARTS.values())[list(PARTS).index(key) + 1:]
    return after.split("\n\n" + later[0] + ":\n")[0] if later else after


class StandIn(GenericFakeChatModel):
    """A stand-in for the model: it plays the messages it is given, in order, and takes any tools it is bound to."""
    def bind_tools(self, tools, **kwargs):
        return self
