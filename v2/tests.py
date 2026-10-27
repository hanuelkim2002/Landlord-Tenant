"""The checks that need no model: the quote checker, the skill quote checker, count_days, the timeline, and the
split of a reply into its short answer and its points.
Run from this folder: python tests.py   (every line should say OK)
"""
import atexit
import json
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path

import chat
import checks
import config
import law
import record
from tools import count_days, save_line

failures = 0


def check(name, passed):
    """Print one result and count a failure."""
    global failures
    failures += not passed
    print(f"{'OK  ' if passed else 'FAIL'} {name}")


# ---- The quote checker (checks.py), on replies made up for the test

LEASE = [{"page": 1, "text": "7. NOTICES TO LANDLORD. Written notices to Landlord shall be delivered by hand to the "
                             "office, or sent there by certified mail.\n8. NOTICES TO TENANT. Notices go to the apartment."}]


def quotes(reply):
    """The quote results for a reply on the test lease."""
    return checks.check_reply(reply, LEASE)["quotes"]


right = quotes('The law: "If the landlord fails to give the required written notice within the 30-day period, he or '
               'she forfeits the right to impose a claim upon the security deposit" (83.49(3)(a)).')
check("a statute quote word for word checks out in the section it cites",
      right[0]["ok"] and right[0]["where"] == "Fla. Stat. 83.49(3)(a)")
changed = quotes('The landlord is "relieved of the notice requirement of paragraph (3)(a)" (83.49(5)).')
check("a quote with one word changed does not check out", not changed[0]["ok"])
elsewhere = quotes('"Failure to give such notice relieves the landlord of the notice requirement" (83.49(3)(a)).')
check("a quote cited to the wrong subsection does not check out", not elsewhere[0]["ok"])
check("a lease quote checks out in the lease",
      quotes('Your lease says "delivered by hand to the office, or sent there by certified mail" (Lease section 7).')[0]["where"]
      == "the lease")
check("a bracketed change and bold marks are not counted as changes",
      quotes('It "forfeit[s] the right to impose a claim upon the **security deposit**" (83.49(3)(a)).')[0]["ok"])
check("a short quotation (under 20 characters) is not checked", quotes('It is "certified mail" here.') == [])
first = quotes('Under 83.49(5), failing to give notice "relieves the landlord of the notice requirement of paragraph (3)(a)."')
check("a statute quote whose cite comes first checks out", first[0]["ok"] and first[0]["where"] == "Fla. Stat. 83.49(5)")
two = quotes('Under the "Notices" part of your lease, it says "delivered by hand to the office, or sent there by '
             'certified mail."')
check("the words between two quotations are not taken as a quote",
      [q["quote"] for q in two] == ["delivered by hand to the office, or sent there by certified mail."] and two[0]["ok"])
cited = checks.check_reply("See 83.49(5) and Lease section 7.", LEASE)["cited"]
check("the cited statute words are the cited subsection", cited[0]["words"].startswith("(5) Except when otherwise"))
check("the cited lease words are the cited section", cited[1]["words"].startswith("7. NOTICES TO LANDLORD")
      and "NOTICES TO TENANT" not in cited[1]["words"])
check("a cite to a section the lease lacks says so",
      "no such section" in checks.check_reply("See Lease section 12.", LEASE)["cited"][0]["words"])

# ---- The skill quote checker (law.py)

check("every skill in skills/ has every quote word for word", law.check_all_skills())
made_up = law.check_quotes('"the landlord must return the deposit within 10 days" (83.49(3)(a))')
check("a made-up quote in a skill is caught", made_up and not made_up[0][2])
wrong_part = law.check_quotes('"must give at least 7 days’ written notice by certified mail" (83.49(3)(a))')
check("a real quote cited to the wrong paragraph is caught", wrong_part and not wrong_part[0][2])
check("a cite finds its paragraph", law.cited_text("83.49(3)(b)").startswith("(b) Unless the tenant objects"))
check("the history note is not part of the cited words", "History" not in law.cited_text("83.505(6)"))

# ---- count_days (tools.py), with facts made up for the test

MATTER = {"confirmed": {name: {"value": value} for name, value in {
    "old_date": "2001-01-01", "future_date": "2099-01-01", "move_out_date": "2026-06-15",
    "leap_date": "2028-02-20", "not_a_date": "July 31"}.items()}}

check("30 days after a past date: the date, and it has passed",
      "= 2001-01-31, which has passed" in count_days(MATTER, "old_date", 30))
check("15 days after a future date has not passed",
      "= 2099-01-16, which has not passed" in count_days(MATTER, "future_date", 15))
check("a negative count goes back: 7 days before 2026-06-15 is 2026-06-08",
      "- 7 days = 2026-06-08" in count_days(MATTER, "move_out_date", -7))
check("counting runs across the end of February in a leap year",
      "= 2028-03-01" in count_days(MATTER, "leap_date", 10))
check("an unconfirmed fact cannot be counted from",
      "not a confirmed fact" in count_days(MATTER, "lease_end_date", 30))
check("a confirmed fact that is not a YYYY-MM-DD date is refused", "not a date" in count_days(MATTER, "not_a_date", 5))
check("every result says the counting is not yet checked",
      "has not been checked against the statute yet" in count_days(MATTER, "old_date", 1))

# ---- The timeline (record.py), in a throwaway matters folder, never the real matters/

config.MATTERS = Path(tempfile.mkdtemp(prefix="matters_test_"))
atexit.register(shutil.rmtree, config.MATTERS, ignore_errors=True)


def refused(action):
    """Whether an action is refused with a ValueError."""
    try:
        action()
    except ValueError:
        return True
    return False


lines_matter = record.new_matter("t-lines", "test")
check("a new matter starts with no lines", lines_matter["lines"] == {})
first = record.save_line(lines_matter, 0, "2026-10-13", "AC stopped working", True)
second = record.save_line(lines_matter, 0, "", "Tenant texted the landlord about the AC", False)
check("new lines are numbered in order", (first, second) == (1, 2))
record.save_line(lines_matter, 1, "2026-10-14", "AC stopped working", True)
versions = [e["date"] for e in record.events(lines_matter) if e["kind"] == "line_saved" and e["number"] == 1]
check("a new version replaces the line, and the history keeps both",
      record.load("t-lines", lines_matter["matter"])["lines"]["1"]["date"] == "2026-10-14"
      and versions == ["2026-10-13", "2026-10-14"])
check("an unknown line number is refused", refused(lambda: record.save_line(lines_matter, 9, "", "x", False)))
check("a line with nothing in it is refused", refused(lambda: record.save_line(lines_matter, 0, "", "  ", False)))
old_matter = record.new_matter("t-old", "test")
saved = json.loads((record.folder(old_matter) / "matter.json").read_text())
saved.pop("lines")
(record.folder(old_matter) / "matter.json").write_text(json.dumps(saved))
check("a matter saved before lines existed opens with no lines",
      record.load("t-old", old_matter["matter"])["lines"] == {})


def add_event(m, time, kind, **data):
    """Write one event with a chosen time, as if it happened then."""
    with (record.folder(m) / "events.jsonl").open("a") as f:
        f.write(json.dumps({"time": time, "kind": kind, **data}) + "\n")


visit = record.new_matter("t-visit", "test")
check("a matter with no messages yet has no last visit", record.since_last_visit(visit, date(2026, 10, 25)) is None)
add_event(visit, "2026-10-13T19:00:00", "message", role="user", text="hi")
add_event(visit, "2026-10-13T19:00:05", "message", role="assistant", text="hello")
add_event(visit, "2026-10-15T09:00:00", "fact_confirmed", fact="move_out_date", value="2026-07-30",
          noted_value="2026-07-31")
add_event(visit, "2026-10-15T09:01:00", "fact_confirmed", fact="deposit", value="800", noted_value="800")
since = record.since_last_visit(visit, date(2026, 10, 25))
check("the days since the last message are counted by code", since["days"] == 12)
check("facts confirmed since then are listed, with the value first noted", since["changed"] == [
    {"fact": "move_out_date", "value": "2026-07-30", "noted_value": "2026-07-31"},
    {"fact": "deposit", "value": "800", "noted_value": "800"}])
check("no block on the same day", record.since_last_visit(visit, date(2026, 10, 13)) is None)
late = record.new_matter("t-late", "test")
add_event(late, "2026-10-24T23:30:00", "message", role="assistant", text="night")
check("a message late last night counts as one day", record.since_last_visit(late, date(2026, 10, 25))["days"] == 1)

# ---- The save_line tool (tools.py)

tool_matter = record.new_matter("t-tool", "test")
check("the tool adds a line and says its number",
      save_line(tool_matter, 0, "2026-10-20", "Landlord texted: fix Thursday", True).startswith("Saved line 1:"))
save_line(tool_matter, 0, "Today", "Tenant got the landlord's letter", "false")
check("'today' becomes today's date, written by code", tool_matter["lines"]["2"]["date"] == str(date.today()))
check("open given as the word false is not open", tool_matter["lines"]["2"]["open"] is False)
check("a number given as text works",
      save_line(tool_matter, "1", "2026-10-21", "Landlord texted: fix Thursday", True).startswith("Saved line 1:"))
check("an unknown number gets a plain reply", "No line 7" in save_line(tool_matter, 7, "", "x", False))
reminder = save_line(tool_matter, 0, "", "Tenant asked for a repair", True)
check("the reply lists the lines still open, so the model can close one the news settles",
      "Still open: line 1, 2026-10-21: Landlord texted: fix Thursday; line 3, no date: Tenant asked for a repair."
      in reminder and "Tenant got the landlord's letter" not in reminder)
save_line(tool_matter, 1, "2026-10-21", "Landlord texted: fix Thursday", False)
check("with no line open, the reply says so",
      "No line is open now." in save_line(tool_matter, 3, "", "Tenant asked for a repair", False))

# ---- The timeline and since-last-visit blocks of the prompt (chat.py)

check("the timeline shows each line in order, open ones marked",
      chat.timeline_text({"1": {"date": "2026-10-13", "what": "AC stopped working", "open": True},
                          "2": {"date": "", "what": "Tenant texted the landlord", "open": False}})
      == "- 1. 2026-10-13: AC stopped working (open)\n- 2. (no date): Tenant texted the landlord")
check("no lines yet says so", chat.timeline_text({}) == "- none yet")
check("no gap, no block", chat.since_text(None) == "")
check("the block gives the days, and the facts confirmed since, with any correction",
      chat.since_text({"days": 12, "changed": [
          {"fact": "move_out_date", "value": "2026-07-30", "noted_value": "2026-07-31"},
          {"fact": "deposit", "value": "800", "noted_value": "800"}]})
      == "\n\nSINCE LAST VISIT (counted by code):\nThe last message was 12 days ago. Since then the tenant confirmed:"
         "\n- move_out_date: 2026-07-30 (first noted as 2026-07-31)\n- deposit: 800")
check("one day is said as one day", chat.since_text({"days": 1, "changed": []})
      == "\n\nSINCE LAST VISIT (counted by code):\nThe last message was 1 day ago.")
# The block's heading, not the words alone: rule 10 names the block too.
TIMELINE_BLOCK, SINCE_BLOCK = "TIMELINE (what happened", "SINCE LAST VISIT (counted by code)"
returning = chat.system_prompt(visit, [])
check("a returning tenant's prompt holds the timeline and the since-last-visit block",
      TIMELINE_BLOCK in returning and SINCE_BLOCK in returning)
check("a brand-new matter's prompt has no since-last-visit block",
      SINCE_BLOCK not in chat.system_prompt(record.new_matter("t-new", "test"), []))

# ---- Splitting a reply into the short answer and its points (chat.py)

check("each heading under DETAILS becomes a point, its title without the # and bold marks",
      chat.split_reply("You get the deposit back.\n\nWhen did you move out?\n\nDETAILS\n### Does the law cover you?\n"
                       "Yes.\n## **Why your landlord loses the deposit**\nNo letter came.")
      == ("You get the deposit back.\n\nWhen did you move out?",
          [("Does the law cover you?", "Yes."), ("Why your landlord loses the deposit", "No letter came.")]))
check("DETAILS with no heading gives one Why point",
      chat.split_reply("Short.\nDETAILS\nAll the reasons.")
      == ("Short.", [("Why, and the law behind it", "All the reasons.")]))
check("text before the first heading goes in the Why point",
      chat.split_reply("Short.\nDETAILS\nFirst.\n### Point?\nBody.")
      == ("Short.", [(chat.WHY, "First."), ("Point?", "Body.")]))
check("no DETAILS line: the whole reply, no points",
      chat.split_reply("All of it.\n### A heading\nBody.") == ("All of it.\n### A heading\nBody.", []))
check("DETAILS inside a sentence is not the marker",
      chat.split_reply("These DETAILS matter.\nMore.") == ("These DETAILS matter.\nMore.", []))
check("the marker may be bold, end in a colon, or be in any case",
      all(chat.split_reply(f"Short.\n{marker}\nWhy.") == ("Short.", [(chat.WHY, "Why.")])
          for marker in ("**DETAILS**", "DETAILS:", "Details", "  details  ")))
check("a heading with nothing under it gives no empty box",
      chat.split_reply("Short.\nDETAILS\n### Empty\n### Full\nBody.") == ("Short.", [("Full", "Body.")]))

print(f"\n{'All checks passed.' if not failures else f'{failures} checks failed.'}")
sys.exit(1 if failures else 0)
