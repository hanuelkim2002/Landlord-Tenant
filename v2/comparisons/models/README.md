# Model comparison

Does a stronger model than nemotron follow the rules and skills better, answer lease questions better, and read
lease pages better? Four chat models and four readers, each run through v2's own code, on two sets of leases.

| Name | Model | Gateway | Role |
| --- | --- | --- | --- |
| nemotron | `nemotron-3-super-120b-a12b` | UF | chat, the baseline |
| gemma | `gemma-4-31b-it` | UF | reader, the baseline |
| haiku | `anthropic/claude-haiku-5.5` | OpenRouter | chat and reader |
| gemini | `google/gemini-3.8-flash` | OpenRouter | chat and reader |
| sonnet | `anthropic/claude-sonnet-5.5` | OpenRouter | chat and reader, the "big model" check |

## The two lease sets

- **sample**: the made-up leases of the earlier tests. The skills test's `lease.txt` for the stories, and the four
  test leases of `comparisons/lease/` for the questions. v1's sample lease is left out: it is kept out of git and
  may be a real lease, so it does not go to OpenRouter.
- **own**: the author's own lease (32 pages, a Florida NAA student housing lease), in `private/`, which git ignores.
  The guarantor's details on page 15 are blacked out before any model sees it. Its keys are in `private/` too.

The own lease showed a problem before any model ran: PyMuPDF reads its printed text, but the typed-in values (name,
rent, dates, notice days, check boxes) and some printed lines (paragraph 27's "via certified mail or personal
delivery at our address only") come out as symbols. The pages still pass `lease.usable`, so the app never reads
them from the image. Only pages 13 and 14 go to Gemma.

## The three tests

1. **Rules and skills** (`run_chat.py stories`). The five deposit stories, 3 runs each, through `chat.run_loop` with
   the system prompt the page builds. The skill is not loaded for the model: it must call `load_skill`, as on the
   page. For the own lease, the stories are rewritten with its facts ($150 deposit, a term ending 2027-07-31,
   paragraph 27's forwarding-address rule) and dated a year later (`private/own_stories.json`).
2. **Lease questions** (`run_chat.py questions`). The sample: 51 questions on the four test leases, from
   `comparisons/lease/answer_key.json`. The own lease: 17 questions (`private/own_questions.json`), 2 of them not
   covered by the lease. One run each.
3. **Reading pages** (`read_pages.py`). Each reader reads pages from their images with the app's own prompt. The
   sample: the scanned lease (4 pages) and the broken one (3 pages), 3 runs each. The own lease: all 32 pages, once,
   scored on 71 values, boxes, and dropped lines read off the page images (`private/own_fields.json`), with PyMuPDF's
   text layer scored the same way as the baseline. Then the broken lease's and the own lease's questions are answered
   by nemotron from each reader's text, to see what better reading changes.

The order matters for the own lease: test 3 runs first. Tests 1 and 2 on the own lease use the best reader's text
(`private/text_own_best.json`), so the chat models are compared on the same, complete text; one extra nemotron run
on the app's own reading (`--texts app`) shows what the page gives today.

## How it is scored

- **By the judge**, `gpt-oss-120b` on UF (not a tested model), by meaning, with the same prompts as the skills and
  lease tests. I review its grades (`review.json`, `private/review.json`). It is weaker than Sonnet, so it may miss a
  subtle error in a strong answer.
- **By the author, blind**: each story's first-run answers from the four models, as W, X, Y, Z (`blind/`, and
  `private/blind/` for the own lease).
- **By code**, one check per rule where code can check it: answers first (rule 2), quotes word for word (rule 6),
  no date the model worked out (rule 7), at most one question (rule 8), the skill loaded, `count_days` used; for
  readers, words right, check boxes right, and what changes between runs. Time and cost for everything.
- Stories 2 and 5 are shown apart: their keys turn on the author's open calls (AUTHOR.md items 3 and 4).

## Cost

Prompt caching is on for the OpenRouter models (`models.py`): the long system prompt is marked so the provider
keeps it after the first send, and resends cost much less. Answers do not change. Expected spend, about $7 to $11 on
OpenRouter; nemotron, Gemma, and the judge run on UF.

## Results (2026-10-21)

`SCORES.md` (numbers only, both sets), `scores.json`, and `private/SCORES_own_detail.md` (each own-lease answer).
Spent: $8.46 on OpenRouter. My review changed 79 of the judge's grades (`review.json`, `private/review.json`), most
because its prompt had only 83.49 and 83.505, or counted a right statute point the lease does not state as an error.

- Stories 1, 3, 4 (18 answers per model, both leases): gemini and sonnet 18, haiku 13 (1 partly), nemotron 11 (2
  partly). Skill loaded: nemotron 4 of 30, the others 30 of 30.
- Lease questions (68 per model): haiku and sonnet 68, gemini 67 (1 partly), nemotron 58.
- Reading the own lease (71 values and boxes): the app today 26, gemma 51, gemini, haiku, and sonnet 71. Haiku is the
  fastest and cheapest of the three (6 s, $0.0014 a page).
- The page's quote check misses right quotes (TODO.md item 1), so its counts are in brackets in SCORES.md.
- Not yet in: the author's blind ranks and the author's check of the own lease's keys (AUTHOR.md item 9).

## How to run

From `v2/`: `source venv/bin/activate`, then `cd comparisons/models`. Add `--dry` to any command to try it with a
fake model: nothing is sent anywhere, and the made-up results go in a `dry/` folder inside `results/` (delete it by
hand). Rerunning a command picks up where it stopped: saved answers are skipped, failed ones are run again.

    python read_pages.py own gemma               # test 3 first; then gemini, haiku, sonnet
    python read_pages.py own app                 # the app's own reading of the own lease, no model
    python read_pages.py sample gemma            # and the other readers
    python run_chat.py stories sample nemotron   # and haiku, gemini, sonnet
    python run_chat.py questions sample nemotron [--texts gemma --leases broken_text]
    python run_chat.py stories own nemotron      # and questions own, with [--texts app]
    python blind.py sample                       # then own; fill in blind/ranks.json
    python score.py [--show-boxes]               # judges and counts everything saved so far

Runs on OpenRouter print its spend total before and after (it runs a little behind, so the second reading waits
30 seconds).
