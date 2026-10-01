# Rules trial, 2026-09-30 to 2026-10-01

Seven versions of `RULES` (the fixed first part of the system prompt) were run on live scenarios and scored
blind. Version F was adopted as `RULES` on 2026-10-01. This folder is a dated record, not kept current.

## Why

After the harness fixes (code prints deadlines, empty replies retried, duplicate drafts stopped, quotes and
cites checked), the slips left were the model's own wording: saying what the law means, offering next
steps, quotes without marks or source. Two runs of the same setup scored 0.50 and 1.00 slips per reply, so
one run per scenario could not measure a change to the rules. The trial used three runs per scenario per
version and blind scoring.

## Method

- `method/brief.md`: what six designer agents were given (what the model sees, what the program does, the
  slips seen, the goals every version keeps, the constraints). Each designer was assigned one strategy.
- `versions/`: `rules_control.txt` (the seven rules in use since 2026-09-30) and `rules_A.txt` to
  `rules_F.txt`.
- Runs: `method/run_trial.py` (first trial) and `method/run_round.py` (confirmation round) drive
  `dev/live_run.py` with `RULES_FILE` set, each arm under its own scratch tenant (`matters/t-trial-*`,
  `matters/t-confirm-*`), on nemotron-3-super-120b-a12b.
- Scoring: `method/extract.py` and `method/extract_confirm.py` write each run as a blind transcript (who
  produced each part: tenant, model, program) under a shuffled code; `method/rubric.md` defines the slip
  categories; two scorer agents per scenario scored every run independently, without knowing the version.
  A slip counts once per category per reply; the figures are the average of the two scorers.

## Versions

| Version | Strategy | Words |
|---|---|---|
| control | the seven rules in use: reply format first | 620 |
| A | short and positive, only what to do | 330 |
| B | compact rules plus worked example replies | 884 |
| C | fixed reply template with headings | 891 |
| D | a records clerk at a court self-help desk; principles with reasons | 892 |
| E | rules plus a silent pre-send checklist | 891 |
| F | "Not:" / "Instead:" pairs taken from the real slips | 895 |

## Results

First trial: the three original stories (nonpayment notice, repair, deposit claim), 9 runs per version,
63 runs. Scorer agreement 88%.

| Version | Slips per reply | Expected results | Empty replies | Notes |
|---|---|---|---|---|
| control | 0.47 (8 in 17) | 9/9 | 0 | half the slips said what the law means |
| A | 0.22 (4 in 18) | 9/9 | 1 | no law statements; two "you can send it" nudges |
| B | 0.17 (3 in 18) | 9/9 | 0 | |
| C | 0.38 (4.5 in 12) | 9/9 | 3 | the template left the model silent after tool calls |
| D | 0.00 (0 in 18) | 7/9 | 0 | two claim runs asked for the letter's text instead of proposing facts, so the deposit-claim deadlines never appeared |
| E | 0.19 (3.5 in 18) | 9/9 | 0 | |
| F | 0.00 (0 in 18) | 9/9 | 0 | |

Confirmation round: control against F on four stories no version was built from (unannounced entry, rent
increase, leaving early, month-to-month ending), 12 runs each, 24 runs. Scorer agreement 86%.

| Version | Slips per reply | Expected results | Program cautions |
|---|---|---|---|
| control | 0.82 (24.5 in 30) | 9/12 | 11 |
| F | 0.13 (4 in 30); 0.23 counting 3 wrong-subsection quotes the program caught and the scorers missed | 12/12 | 3 |

The control's three misses were the entry letter: asked for a letter with every detail, it asked again for
all of them and never drafted. Most of its cautions came from quote marks around labels and field values.

## Learned

- Showing the model its real past mistakes next to the replacement ("Not:" / "Instead:") worked best on
  this model, on the stories it was built from and on new ones.
- A clean slip score is not enough: D scored zero slips and broke a function (no facts proposed). Expected
  results are measured separately for that reason.
- A rigid template (C) made the model go silent; a role (D) was read literally ("exact words" became asking
  for the document).
- F's own "Instead:" lines can be copied out of context: "then ask: How will you send it?" was asked twice
  when no letter was requested (month-to-month story). A wording fix, not yet made.
- Scorers miss wrong-subsection quotes that `citations.check_quoted` catches; the two measures together
  are better than either.
