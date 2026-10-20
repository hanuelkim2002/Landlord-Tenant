"""The checks that need no model: the quote checker, the skill quote checker, and count_days.
Run from this folder: python tests.py   (every line should say OK)
"""
import sys

import checks
import law
from tools import count_days

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

print(f"\n{'All checks passed.' if not failures else f'{failures} checks failed.'}")
sys.exit(1 if failures else 0)
