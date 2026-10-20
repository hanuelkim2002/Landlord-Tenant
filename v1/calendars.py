"""Court Calendars: the holidays each judicial circuit's courts observe, loaded once from calendars/*.json.

A read-only corpus, like statutes/. Each file is one circuit: its counties and, per year, the holidays listed
in the Chief Judge's memorandum, with the memorandum's source and the date it was fetched (the PDF is kept in
calendars/sources/). Used by deterministic.compute_deadlines for clocks counted in court business days.
Nothing here calls a model, and no date is ever filled in from memory: a year with no memorandum loaded is
refused, not guessed.
"""
import json
from datetime import date

from config import ROOT

CALENDARS = ROOT / "calendars"


def load_calendar(path):
    """Read one circuit's file and check it: every holiday's date falls in its year, and the weekday printed in
    the memorandum is the date's real weekday (entries taken from a note are not printed with a weekday)."""
    cal = json.loads(path.read_text())
    for year, entry in cal["years"].items():
        for h in entry["holidays"]:
            d = date.fromisoformat(h["date"])
            if str(d.year) != year:
                raise ValueError(f"{path.name}: {h['date']} is filed under {year}")
            printed = h["as_printed"].split(",")[0]
            if not h["as_printed"].startswith("Note:") and printed != d.strftime("%A"):
                raise ValueError(f"{path.name}: {h['date']} is printed as {printed}")
    return cal


def court_calendar(county):
    """The calendar of the circuit that includes this county ("Alachua" or "Alachua County"), or None."""
    if not county:
        return None
    name = county.strip().lower().removesuffix(" county").strip()
    return next((c for c in court_calendars if name in [n.lower() for n in c["counties"]]), None)


def holidays_in(cal):
    """Every holiday date in a circuit's calendar, across the years loaded."""
    return {date.fromisoformat(h["date"]) for entry in cal["years"].values() for h in entry["holidays"]}


court_calendars = [load_calendar(p) for p in sorted(CALENDARS.glob("*.json"))]
