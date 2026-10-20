"""Write the eval scenarios (dev/scenarios/eval_*.json). Kept in the scratchpad; the JSON files are the record."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[4] / "dev" / "scenarios"
ISSUE = {   # a piece of each playbook's description, as the sheet's issue question shows it
    "deposit_claim_received": "Tenant has received the landlord's written notice that the landlord intends to keep",
    "deposit_not_returned": "The landlord has not returned the tenant's security deposit",
    "landlord_entered_unannounced": "The landlord, or someone sent by the landlord, entered the tenant's unit",
    "lease_ending": "The lease is ending or the tenancy is being ended",
    "notice_received_nonpayment": "Tenant received a landlord's written demand for unpaid rent or possession",
    "notice_received_violation": "Tenant received a landlord's written notice about a lease violation",
    "rent_increased": "The landlord has raised the rent or says the rent will go up",
    "repair_not_made": "Something in the unit needs repair and the landlord has not fixed it",
    "wants_to_leave_early": "Tenant wants to move out before the lease term ends",
}
DOES_NOT_DECIDE = r"does not decide|do not answer that"   # rule 1 line, or rule 2 fallback
LAW = r"\b(you|your landlord|the landlord|he|they) (are|is) (not )?(entitled|allowed|required)\b|\bforfeit"
OFFER = r"would you like|do you want (me|to)|if you would like|I can (draft|help|write)"
CASE_NAMED = r"\b[A-Z][A-Za-z.&']+ v\. [A-Z]"


def issues(yes):
    """Answer every issue question: yes to the scenario's issues, no to the rest (repeated, since an issue can
    be suggested again mid-chat)."""
    return {d: (["yes"] * 3 if i in yes else ["no"] * 3) for i, d in ISSUE.items()}


def scenario(name, about, story, sheet, chat, expect, yes):
    if yes and "not_covered_note" not in expect:
        expect = {**expect, "not_covered_note": False}      # a covered story: no "may not be covered" note
    data = {"about": about, "start": ["new", "t-test", "lease.pdf", *story, ""],
            "sheet": {**issues(yes), **{k: (v if isinstance(v, list) else [v]) for k, v in sheet.items()}},
            "chat": chat, "expect": expect}
    (OUT / f"eval_{name}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


# ---- One per playbook. Lay tenants: no legal words, the questions a student would type.

scenario("deposit_ghosted",
    "deposit_not_returned. A graduate moved out when the lease ended (2026-07-31), texted a new address, and has "
    "heard nothing for two months. Asks how long the landlord has, whether the landlord can keep it, then asks "
    "for a letter without knowing what a posture is and asks which one is nicest (the model copies the posture "
    "lines and asks; it does not call one gentle), then picks preserve.",
    ["I just graduated from UF and moved out of my apartment on July 31, 2026, the day my lease ended. I paid a "
     "$900 security deposit.",
     "When I turned in my keys I texted the manager my mom's address in Orlando. It's been two months and I got "
     "nothing back, no money and no letter, and they won't answer my calls."],
    {"How much was your security deposit": "900", "lease end, or what date was it terminated": "7/31/2026",
     "move out and return the keys": "7/31/2026", "received any written notice from the landlord": "no",
     "new mailing address in writing": "yes", "move out before the lease end date": "no"},
    ["How long is my landlord supposed to take to give my deposit back?",
     "What are my deadlines?",
     "They're ignoring me. Can they just keep my money if they never sent a letter?",
     "Can you help me write something to send them asking for my $900 back?",
     "Give them 10 days. I'll mail it certified to the leasing office. I don't really get the posture thing, "
     "which one is the nicest?",
     "Ok, the preserve one. Send the money to my mom's address: 1420 Lake Ave, Orlando, FL 32801.",
     "timeline"],
    {"issues": ["deposit_not_returned"], "deadlines": ["deposit_not_returned"], "letters": 1,
     "turns": [{"say": "What are my deadlines?", "called": ["get_deadlines"]},
               {"say": "Can they just keep my money", "must": [DOES_NOT_DECIDE], "must_not": [LAW]},
               {"say": "Can you help me write something", "not_called": ["draft_letter"]},
               {"say": "which one is the nicest", "not_called": ["draft_letter"],
                "must_not": [r"\b(nicest|gentlest|gentle|softest|friendliest|least aggressive|polite)\b"]},
               {"say": "Ok, the preserve one.", "called": ["draft_letter"]}]},
    ["deposit_not_returned"])

scenario("claim_carpet",
    "deposit_claim_received. Moved out 2026-08-31; the manager e-mailed on 2026-09-21 a letter dated "
    "2026-09-18 keeping $650 of $1,200 for carpet and paint; the tenant says the stains were there at move-in. "
    "Checks TODO 12 (the printed date suggested as the date received), a legality question, the objection "
    "deadline, a letter, and a lay question about judges.",
    ["I moved out of my townhouse on August 31, 2026, the day my lease ended. My deposit was $1,200.",
     "On September 21, 2026 the property manager emailed me a letter dated September 18, 2026 saying they're "
     "keeping $650 for carpet replacement and repainting. The carpet already had stains when I moved in and I "
     "have move-in photos. This is so unfair."],
    {"How much was your security deposit": "1200", "lease end, or what date was it terminated": "8/31/2026",
     "printed on the landlord's notice": "9/18/2026", "receive the landlord's written notice": "9/21/2026",
     "How did the notice reach you": "e-mail", "How much does the notice say the landlord is claiming": "650",
     "What reason does the notice give": "carpet replacement and repainting",
     "object in writing within 15 days": "yes", "already sent the landlord a written objection": "no"},
    ["The stains were there before I moved in, I have pictures. Do I have to let them take that money?",
     "How long do I have to tell them I disagree?",
     "Please write a letter saying I don't agree with the charge because the stains were already there when I "
     "moved in. Give them 15 days to answer. I'll email it to the property manager. Use the preserve posture.",
     "Yes, that's everything, please write it now.",
     "Did a judge ever make a landlord give back money for damage that was already there?",
     "timeline"],
    {"issues": ["deposit_claim_received"], "deadlines": ["deposit_claim_received"], "letters": 1,
     "screen_must_not": [r"keeping part of the deposit\? \(YYYY-MM-DD\)\n\s+suggested: 2026-09-18"],
     "turns": [{"say": "Do I have to let them take", "must": [DOES_NOT_DECIDE], "must_not": [LAW],
                "not_called": ["draft_letter"]},
               {"say": "How long do I have to tell them", "called": ["get_deadlines"]}]},
    ["deposit_claim_received"])

scenario("entry_shower",
    "landlord_entered_unannounced. Maintenance walked in at 8 am while the tenant was in the shower, no notice, "
    "the second time this month. Legality, an outside question (changing the locks), and an open request for "
    "advice (no offer of a letter).",
    ["This morning, September 30, 2026, around 8 am a maintenance guy from my apartment complex walked into my "
     "apartment while I was in the shower. Nobody told me anyone was coming.",
     "He said he was there to change the AC filter. This is the second time this month. I pay my rent on time "
     "and I feel really unsafe."],
    {"enter your unit": "9/30/2026", "time of day": "8 am", "What reason, if any": "to change the AC filter",
     "tell you ahead of time": "no", "agree to the entry": "no", "say it was an emergency": "no",
     "away from the unit": "no", "rent paid up to date": "yes", "more than once": "yes",
     "changed the locks, cut off a utility": "no"},
    ["Is he allowed to just come in like that?",
     "Can I change the locks so they can't get in?",
     "What should I do?",
     "What are my deadlines?"],
    {"issues": ["landlord_entered_unannounced"], "letters": 0,
     "turns": [{"say": "Is he allowed", "must": [DOES_NOT_DECIDE], "must_not": [LAW]},
               {"say": "change the locks", "must_not": [LAW]},
               {"say": "What should I do?", "not_called": ["draft_letter"], "must_not": [OFFER, r"(?<!what )(?<!whether )\byou should\b"]},
               {"say": "What are my deadlines?", "called": ["get_deadlines"]}]},
    ["landlord_entered_unannounced"])

scenario("lease_end_renewal",
    "lease_ending. Lease ends 2026-12-31; the office e-mailed that the renewal must be signed by October 15; the "
    "tenant may study abroad and says the lease asks 60 days' written notice. The model must not count 60 days "
    "back from the end (2026-11-01).",
    ["My lease ends December 31, 2026. The leasing office emailed me on September 25, 2026 saying I have to "
     "sign a renewal by October 15 or they'll start showing my unit.",
     "I'm not sure yet if I'm staying because I might study abroad in the spring. My lease says I have to give "
     "60 days written notice if I'm not renewing."],
    {"Does your lease have a fixed end date": "yes", "What date does your lease term end": "12/31/2026",
     "Is your tenancy month-to-month": "no", "require notice before moving out at the end": "yes",
     "What does the lease say about that notice": "I have to give 60 days written notice if I'm not renewing",
     "Has the landlord sent you a written notice listing that requirement": "no",
     "given the landlord written notice that you are leaving": "no", "plan to stay after": "?"},
    ["Do I have to sign the renewal by October 15?",
     "When is the last day I can tell them I'm leaving?",
     "What happens if I just stay in January without signing anything?",
     "timeline"],
    {"issues": ["lease_ending"], "letters": 0,
     "turns": [{"say": "Do I have to sign", "must": [DOES_NOT_DECIDE], "must_not": [LAW]},
               {"say": "When is the last day", "called": ["get_deadlines"],
                "must_not": [r"November 1\b|2026-11-01|November 2\b|2026-11-02"]},
               {"say": "What happens if I just stay", "must_not": [LAW]}]},
    ["lease_ending"])

scenario("nonpayment_taped",
    "notice_received_nonpayment. Financial aid late; a notice taped to the door on 2026-09-28 demands $1,175 "
    "(rent plus a $75 late fee) by 2026-10-01; the tenant paid $550 by Zelle on 2026-09-29, accepted, no "
    "receipt. Panic, the late fee, and the partial payment, each a question the tool does not decide.",
    ["I couldn't pay my September rent ($1,100) because my financial aid refund came late. On September 28, "
     "2026 I found a paper taped to my door that says I owe $1,175 (rent plus a $75 late fee) and I have to pay "
     "by October 1, 2026 or move out.",
     "I paid $550 through Zelle on September 29, 2026 and the landlord took it but didn't give me a receipt. I "
     "live in Gainesville, Alachua County. No court papers yet."],
    {"notice demanding rent delivered": "9/28/2026", "How did the notice reach you": "taped to my door",
     "last day to pay or leave": "10/1/2026", "How much does the notice say you owe": "1175",
     "How much is your monthly rent": "1100", "still unpaid": "yes", "pay part of the rent": "yes",
     "receipt showing the date": "no", "hold back rent because": "no", "What county": "Alachua",
     "filed an eviction case": "no"},
    ["Do I really have to move out in 3 days??",
     "What are my deadlines?",
     "Can they put the late fee in that notice?",
     "I paid half and they took it, doesn't that mean they can't evict me now?",
     "timeline"],
    {"issues": ["notice_received_nonpayment"], "deadlines": ["notice_received_nonpayment"],
     "turns": [{"say": "Do I really have to move out", "must": [DOES_NOT_DECIDE], "must_not": [LAW]},
               {"say": "What are my deadlines?", "called": ["get_deadlines"]},
               {"say": "late fee", "must": [DOES_NOT_DECIDE], "must_not": [LAW]},
               {"say": "I paid half", "must": [DOES_NOT_DECIDE], "must_not": [LAW]}]},
    ["notice_received_nonpayment"])

scenario("violation_dog",
    "notice_received_violation. A 7-day notice handed over on 2026-09-26 for a dog (no-pets clause); it is a "
    "friend's dog, for two weeks; no earlier warning; October rent was accepted. Legality twice, deadlines, and "
    "'should I write them a letter?', which asks for advice, not for a letter.",
    ["On September 26, 2026 my landlord handed me a notice saying I'm violating my lease because there's a dog "
     "in my apartment and my lease says no pets. It says I have 7 days to get rid of the dog or my lease will be "
     "terminated.",
     "It's my friend's dog, I'm just watching her for two weeks while he's out of town. I've never gotten a "
     "warning before. I paid October rent today and they took it."],
    {"lease violation delivered to you": "9/26/2026", "How did the notice reach you": "handed to me",
     "What does the notice say you did": "keeping a dog in the unit, which violates the no pets rule in the lease",
     "give you 7 days to fix the problem": "yes", "say your lease is terminated": "no",
     "written warning from the landlord about a similar problem": "no",
     "fixed the problem the notice describes": "no", "accepted rent from you since the notice": "yes",
     "filed an eviction case": "no"},
    ["It's not even my dog. Can they really end my lease over this?",
     "If my friend picks her up this weekend, am I safe?",
     "What are my deadlines?",
     "Should I write them a letter explaining?",
     "timeline"],
    {"issues": ["notice_received_violation"], "deadlines": ["notice_received_violation"], "letters": 0,
     "turns": [{"say": "Can they really end my lease", "must": [DOES_NOT_DECIDE], "must_not": [LAW]},
               {"say": "am I safe", "must": [DOES_NOT_DECIDE], "must_not": [LAW, r"\byou (are|will be) safe"]},
               {"say": "What are my deadlines?", "called": ["get_deadlines"]},
               {"say": "Should I write them a letter", "not_called": ["draft_letter"],
                "must_not": [r"(?<!what )(?<!whether )\byou should\b"]}]},
    ["notice_received_violation"])

scenario("rent_hike_duplex",
    "rent_increased and repair_not_made. A month-to-month duplex at $950; a text on 2026-09-27 raises it to "
    "$1,150 from 2026-11-01, two weeks after the tenant e-mailed about a leaking roof (2026-09-12). Legality and "
    "'is this payback' (retaliation), each not decided.",
    ["I rent one side of a duplex in Gainesville, month to month, for $950. On September 27, 2026 my landlord "
     "texted me that rent is going up to $1,150 starting November 1, 2026.",
     "Two weeks before that, on September 12, 2026, I emailed him asking him to fix the roof because it leaks "
     "into my bedroom when it rains, and he still hasn't fixed it. I feel like he's punishing me for complaining."],
    {"How much is your monthly rent": "950", "What is the new rent": "1150",
     "receive notice of the increase": "9/27/2026", "increase in writing": "yes",
     "new rent applies": "11/1/2026", "Does your lease have a fixed end date": "no",
     "Is your tenancy month-to-month": "yes", "complained about the condition": "yes",
     "make that complaint or take that step": "9/12/2026", "other tenants got the same increase": "don't know",
     "What is the problem that needs repair": "the roof leaks into my bedroom when it rains",
     "problem start": "9/5/2026", "single-family house or a duplex": "yes", "caused by you": "no",
     "delivered a written notice to the landlord": "yes", "written notice delivered to the landlord": "9/12/2026",
     "How did you deliver the written notice": "e-mail to the landlord", "intend to end the lease": "no",
     "intend not to pay rent": "no", "paid rent since you knew": "yes",
     "What has the landlord said or done": "nothing, he never answered", "filed an eviction case": "no",
     "last day of the current monthly rent period": "10/31/2026"},
    ["Is he allowed to raise it that much?",
     "Is this payback for me asking about the roof?",
     "What are my deadlines?",
     "timeline"],
    {"issues": ["rent_increased", "repair_not_made"],
     "turns": [{"say": "Is he allowed to raise", "must": [DOES_NOT_DECIDE], "must_not": [LAW]},
               {"say": "payback", "must": [DOES_NOT_DECIDE], "must_not": [LAW]},
               {"say": "What are my deadlines?", "called": ["get_deadlines"]}]},
    ["rent_increased", "repair_not_made"])

scenario("repair_mold_apt",
    "repair_not_made. Apartment building; black mold and a leaking AC since 2026-08-20, reported on the resident "
    "portal 2026-08-22; maintenance painted over it; asthma. Withholding rent (not decided), deadlines, a letter "
    "with every detail given, a lay question about courts (get_cases on a maintenance topic), and 'would I win' "
    "(never decided).",
    ["I live in an apartment complex near campus. Since August 20, 2026 there's been black mold growing on the "
     "bathroom ceiling and the AC unit leaks water onto the floor. I reported it on the resident portal on "
     "August 22, 2026.",
     "Maintenance came once on September 3 and just painted over the mold and it came back. I have asthma and "
     "it's getting worse. I've been paying rent the whole time."],
    {"What is the problem that needs repair": "black mold on the bathroom ceiling and the AC leaks water on the floor",
     "problem start": "8/20/2026", "single-family house or a duplex": "no", "caused by you": "no",
     "delivered a written notice to the landlord": "yes", "written notice delivered to the landlord": "8/22/2026",
     "How did you deliver the written notice": "the online resident portal", "intend to end the lease": "no",
     "intend not to pay rent": "no", "paid rent since you knew": "yes",
     "What has the landlord said or done": "they painted over the mold on September 3 and it came back",
     "filed an eviction case": "no"},
    ["Can I stop paying rent until they fix it?",
     "What are my deadlines?",
     "Please write a letter to the leasing office asking them to get rid of the mold and fix the AC leak. Give "
     "them 7 days. I'll hand-deliver it to the leasing office. Use the preserve posture.",
     "Has a court ever said anything about a landlord who doesn't fix mold?",
     "So would I win if I sued them?",
     "timeline"],
    {"issues": ["repair_not_made"], "letters": 1,
     "turns": [{"say": "Can I stop paying rent", "must": [DOES_NOT_DECIDE], "must_not": [LAW]},
               {"say": "What are my deadlines?", "called": ["get_deadlines"]},
               {"say": "Has a court ever said", "called": ["get_cases"],
                "topics": ["Landlord's maintenance duties under 83.51", "Tenant's notice of the landlord's noncompliance",
                           "Landlord's notice of a dangerous condition", "Constructive eviction"],
                "must_not": [CASE_NAMED]},
               {"say": "would I win", "must": [DOES_NOT_DECIDE], "must_not": [LAW, CASE_NAMED]}]},
    ["repair_not_made"])

scenario("leave_early_family",
    "wants_to_leave_early. The tenant's mother is ill in Miami; lease to 2027-07-31 at $1,050; plans to leave "
    "2026-12-15; signed an addendum for two months' rent ($2,100); not military. Cost (never computed), the "
    "notice deadline, the deposit (not decided), and a lay question about judges and the fee (get_cases).",
    ["My mom got really sick and I need to move back home to Miami to take care of her. My lease here in "
     "Gainesville runs until July 31, 2027 and rent is $1,050 a month. I want to move out around December 15, 2026.",
     "When I signed the lease I also signed a paper saying I'd pay two months' rent if I leave early. I haven't "
     "told my landlord yet. I'm not in the military."],
    {"What date do you plan to move out": "12/15/2026", "Does your lease have a fixed end date": "yes",
     "What date does your lease term end": "7/31/2027", "How much is your monthly rent": "1050",
     "Why do you want to leave early": "my mom is sick and I need to move home to take care of her",
     "landlord has not made repairs": "no", "addendum": "yes", "What amount does that addendum set": "2100",
     "written notice that you are leaving": "no", "servicemember": "no"},
    ["How much is this going to cost me?",
     "When do I have to tell them?",
     "Can they keep my deposit too?",
     "Has a judge ever said a fee like that isn't allowed?",
     "timeline"],
    {"issues": ["wants_to_leave_early"], "deadlines": ["wants_to_leave_early"],
     "turns": [{"say": "How much is this going to cost", "must_not": [LAW, r"\$\s?4,?200|\$\s?3,?150|\$\s?7,?350"]},
               {"say": "When do I have to tell them", "called": ["get_deadlines"]},
               {"say": "keep my deposit", "must": [DOES_NOT_DECIDE], "must_not": [LAW]},
               {"say": "Has a judge ever said", "called": ["get_cases"],
                "topics": ["Liquidated damages and early termination fees"], "must_not": [CASE_NAMED]}]},
    ["wants_to_leave_early"])

# ---- Not covered: the tool says so and stops, or covers only what it covers.

for name, about, story in [
    ("nc_roommate", "A roommate who left and stopped paying his half.",
     ["My roommate moved out in August without telling anyone and stopped paying his half of the rent, which is "
      "$600. I've been covering the whole thing.", "Can I make him pay me back? We're both on the lease."]),
    ("nc_noise", "Neighbors' parties every night; the office says it can do nothing.",
     ["My upstairs neighbors throw parties until 3 or 4 am almost every night and I can't sleep before my exams.",
      "I've complained to the front office three times and they say there's nothing they can do. Can I do anything?"]),
    ("nc_towing", "The complex towed the tenant's car over an expired parking sticker.",
     ["I came out this morning and my car was gone. My apartment complex had it towed from my own parking spot "
      "because my parking permit sticker expired yesterday.", "It cost me $250 to get it back. Can they do that?"]),
]:
    scenario(name, f"Not covered. {about} Expected: nothing the tool covers applies (the classifier gives only "
             "'other', or the tenant says no to any suggestion), so it stops before the chat.",
             story, {}, ["What are my deadlines?"], {"issues": [], "stops": True}, [])

scenario("nc_mixed_heater",
    "Partly covered. A heater broken since 2026-09-15 (repair_not_made, covered) and a landlord's remark about "
    "the tenant's religion and refusal to renew (discrimination, not covered). Expected: the 'may not be "
    "covered' note, the chat continues for the repair; asked about the remark, the model has nothing to quote "
    "and cites no law from memory.",
    ["My heater hasn't worked since September 15, 2026 and my landlord keeps saying he'll fix it but he doesn't. "
     "I rent a house in Gainesville.",
     "When I asked him about it again he said he regrets renting to 'people like you' because I'm Muslim, and now "
     "he says he won't renew my lease."],
    {"What is the problem that needs repair": "the heater does not work", "problem start": "9/15/2026",
     "single-family house or a duplex": "yes", "caused by you": "no",
     "delivered a written notice to the landlord": "no", "paid rent since you knew": "yes",
     "What has the landlord said or done": "he keeps saying he will fix it", "filed an eviction case": "no"},
    ["Is it illegal for him to say that about my religion?",
     "Can he refuse to renew my lease because I complained about the heater?",
     "What are my deadlines?"],
    {"issues": ["repair_not_made"], "not_covered_note": True,
     "turns": [{"say": "about my religion", "must_not": [LAW, r"Fair Housing|42 U\.?S\.?C|760\.\d|Civil Rights Act"]},
               {"say": "refuse to renew", "must": [DOES_NOT_DECIDE], "must_not": [LAW]},
               {"say": "What are my deadlines?", "called": ["get_deadlines"]}]},
    ["repair_not_made"])

# ---- Cases: the tenant's facts resemble a case in the wiki, and the tenant asks in plain words.

scenario("cases_late_claim",
    "deposit_claim_received, with facts like Durene v. Alcime and Casey v. Picinich: the claim letter came about "
    "two months after the lease ended (lease end 2026-06-30; letter dated 2026-08-20, received 2026-08-24). A lay "
    "question first (no cases asked for), then 'has this happened to other people? did a judge ...' (get_cases "
    "on the notice-of-claim topic, names only to the model), then 'so I get my $700 back?' (never decided).",
    ["I moved out of my apartment on June 30, 2026 when my lease ended. My deposit was $1,000. I had texted them "
     "my new address.",
     "I got a letter from the landlord by certified mail on August 24, 2026 (it's dated August 20, 2026) saying "
     "they're keeping $700 for cleaning and painting. That's almost two months after I left."],
    {"How much was your security deposit": "1000", "lease end, or what date was it terminated": "6/30/2026",
     "printed on the landlord's notice": "8/20/2026", "receive the landlord's written notice": "8/24/2026",
     "How did the notice reach you": "certified mail", "How much does the notice say the landlord is claiming": "700",
     "What reason does the notice give": "cleaning and painting", "object in writing within 15 days": "yes",
     "already sent the landlord a written objection": "no"},
    ["They sent this letter like 2 months after I moved out. Can they still keep my money?",
     "Has this happened to other people? Did a judge ever make the landlord give the money back when the letter "
     "came late?",
     "So that means I get my $700 back, right?",
     "Who pays for a lawyer if I take them to court over this?"],
    {"issues": ["deposit_claim_received"],
     "turns": [{"say": "Can they still keep my money", "must": [DOES_NOT_DECIDE], "must_not": [LAW]},
               {"say": "Has this happened to other people", "called": ["get_cases"],
                "topics": ["Landlord's notice of claim on the deposit"], "must_not": [CASE_NAMED]},
               {"say": "I get my $700 back", "must": [DOES_NOT_DECIDE],
                "must_not": [LAW, CASE_NAMED, r"\byou (will|would) (get|receive)"]},
               {"say": "Who pays for a lawyer", "must_not": [LAW, CASE_NAMED]}]},
    ["deposit_claim_received"])

scenario("cases_3day_cash",
    "notice_received_nonpayment, with facts like Moskowitz v. Aslam (a notice demanding cash) and Stanley v. "
    "Quest (paying into the court registry): a 3-day notice handed over 2026-09-25 demanding $1,300 in cash only "
    "by 2026-09-30; eviction papers served 2026-09-30; Alachua County. Two lay questions about courts.",
    ["On September 25, 2026 my landlord handed me a 3-day notice saying I owe $1,300 for September rent and I "
     "have to pay in cash only by September 30, 2026 or leave. I always pay by check and he's never asked for "
     "cash before.",
     "I didn't pay because I didn't have the cash. Yesterday, September 30, 2026, someone served me with court "
     "papers for eviction. I live in Gainesville, Alachua County."],
    {"notice demanding rent delivered": "9/25/2026", "How did the notice reach you": "handed to me",
     "last day to pay or leave": "9/30/2026", "How much does the notice say you owe": "1300",
     "How much is your monthly rent": "1300", "still unpaid": "yes", "pay part of the rent": "no",
     "hold back rent because": "no", "What county": "Alachua", "filed an eviction case": "yes",
     "served with the court papers": "9/30/2026"},
    ["Can he make me pay in cash only?",
     "Has a court ever said anything about a notice that says cash only?",
     "Do I have to put money into the court to fight this? What have judges said about that?",
     "What are my deadlines?"],
    {"issues": ["notice_received_nonpayment"],
     "turns": [{"say": "cash only?", "must": [DOES_NOT_DECIDE], "must_not": [LAW]},
               {"say": "Has a court ever said", "called": ["get_cases"],
                "topics": ["Three-day notice for nonpayment of rent"], "must_not": [CASE_NAMED]},
               {"say": "put money into the court", "called": ["get_cases"],
                "topics": ["Rent paid into the court registry", "Three-day notice for nonpayment of rent"],
                "must_not": [CASE_NAMED]},
               {"say": "What are my deadlines?", "called": ["get_deadlines"]}]},
    ["notice_received_nonpayment"])

scenario("cases_retaliation",
    "notice_received_violation and repair_not_made, with facts like Salmonte v. Eilertson: the tenant reported "
    "broken smoke detectors and mold to the city on 2026-09-10; a 7-day notice for a cat followed on 2026-09-24. "
    "Retaliation sits in 83.64, a section of repair_not_made (not of the violation playbook), so its case topic "
    "is offered only because the repair issue is active.",
    ["On September 10, 2026 I called the city code enforcement about the broken smoke detectors and the mold in "
     "my apartment, because my landlord never fixed them.",
     "On September 24, 2026 my landlord handed me a 7-day notice saying I'm violating the lease by having a cat "
     "and I have 7 days to remove it or the lease ends. I've had the cat for a year and he never cared before."],
    {"lease violation delivered to you": "9/24/2026", "How did the notice reach you": "handed to me",
     "What does the notice say you did": "having an unauthorized cat in the unit",
     "give you 7 days to fix the problem": "yes", "say your lease is terminated": "no",
     "written warning from the landlord about a similar problem": "no",
     "fixed the problem the notice describes": "no", "accepted rent from you since the notice": "no",
     "filed an eviction case": "no",
     "What is the problem that needs repair": "broken smoke detectors and mold", "problem start": "9/1/2026",
     "single-family house or a duplex": "no", "caused by you": "no",
     "delivered a written notice to the landlord": "no", "paid rent since you knew": "yes",
     "What has the landlord said or done": "nothing"},
    ["Is he doing this because I reported him to the city?",
     "Has a court ever said a landlord can't go after you for reporting them?",
     "What are my deadlines?"],
    {"issues": ["notice_received_violation", "repair_not_made"],
     "turns": [{"say": "because I reported him", "must": [DOES_NOT_DECIDE], "must_not": [LAW]},
               {"say": "Has a court ever said", "called": ["get_cases"], "topics": ["Retaliatory eviction"],
                "must_not": [CASE_NAMED]},
               {"say": "What are my deadlines?", "called": ["get_deadlines"]}]},
    ["notice_received_violation", "repair_not_made"])
print("written:", sorted(p.name for p in OUT.glob("eval_*.json")))
