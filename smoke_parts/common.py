"""Helpers shared by the smoke parts: a phrase of 83.49(3)(a) the quote checks use, and small helpers for the
checks that write to a matter. (Named checks and scratch matters are in checks.py.)"""
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel

from prompt import PARTS, system_prompt

FORFEIT = "he or she forfeits the right to impose a claim upon the security deposit"     # in 83.49(3)(a)


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
    """One part of the system prompt as it stands now (prompt.PARTS), without its name."""
    after = system_prompt().split("\n\n" + PARTS[key] + ":\n")[1]
    later = list(PARTS.values())[list(PARTS).index(key) + 1:]
    return after.split("\n\n" + later[0] + ":\n")[0] if later else after


class StandIn(GenericFakeChatModel):
    """A stand-in for the model: it plays the messages it is given, in order, and takes any tools it is bound to."""
    def bind_tools(self, tools, **kwargs):
        return self
