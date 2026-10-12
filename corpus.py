"""The stored statute, and what the other modules share about a deadline clock. Statute text keyed by section; Clock,
the shape of one statutory deadline (skills.py reads it from a skill's header); report, the line a check prints.

The statute is loaded once when this module is imported. Nothing here calls a model.
"""
from typing import Literal, Optional

from pydantic import BaseModel

from config import STATUTES


# ---- Load Statutes: one entry per section, keyed by number ("83.49").

statute = {p.stem: p.read_text() for p in STATUTES.glob("83.*.txt")}


# ---- Clock Shape: the one typed part of a skill that code computes from.

class Clock(BaseModel):
    """One statutory deadline: whose it is, which date it counts from, how many
    days, and the sentence it comes from. compute_deadlines reads these. count: calendar days (the default)
    or court business days, which skip Saturdays, Sundays, and the county's court holidays (calendars.py).
    shown_with names a date fact printed next to the computed date once confirmed, such as the date the
    notice itself states, so the tenant sees both. condition: what the date counts only if, in words, printed with
    it, when it counts from a paper whose sufficiency the tool does not decide (a notice the tenant sent)."""
    id: str
    actor: Literal["landlord", "tenant"]
    trigger: str
    days: int
    direction: Literal["before", "after"]
    cite: str
    quote: str
    consequence: Optional[str] = None
    applies_if: Optional[str] = None
    count: Literal["calendar_days", "court_business_days"] = "calendar_days"
    shown_with: Optional[str] = None
    condition: Optional[str] = None


def report(name, ok):
    """Print one check line, OK or FAIL, and return 1 for a failure so callers can count them."""
    print(("OK   " if ok else "FAIL ") + name)
    return 0 if ok else 1
