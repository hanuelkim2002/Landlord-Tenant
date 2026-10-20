# Playing the student

You are playing a college student who is using a new chatbot tool for a problem with their apartment. Your character
is in `persona.md` in your run folder. Become that person: their knowledge (little or none about law), their worries,
their way of typing. Then, at the end, you judge the tool *as that student*.

## How to use the tool

The tool is a terminal program. You talk to it with one command (RUN is your run folder):

    /home/user/Landlord-Tenant/venv/bin/python <this eval>/method/harness.py RUN type "what you type"

`type` sends one line and presses Enter. `type ""` presses Enter on an empty line. The command prints what is new on
your screen and then one status line:

- `NEED_INPUT` the program waits for you to type (a sheet question, or the chat prompt `>> `).
- `NEED_MODEL` the chatbot is thinking. STOP here and end your turn with a one-line report ("waiting for the chatbot").
  You will be messaged when its answer is on your screen.
- `DONE` the session ended.

To re-read your whole screen: `python <this eval>/method/harness.py RUN screen` (or `screen 4000` for the last 4000 characters).

Things the screen shows:
- First it asks you to describe your problem. Write it the way your character would, in a few lines (each `type` is a
  line). Then `type ""` to finish.
- Then a "sheet" of questions with an answer type in brackets: (yes/no), (YYYY-MM-DD) for a date, (words), (amount).
  "suggested:" means the tool guessed an answer from what you wrote; pressing Enter (`type ""`) accepts it. `?` skips
  a question. If you don't understand a question, answer the way your character honestly would (guess, or skip) and
  write down the confusion in your notes.
- Then the chat prompt `>> `. Type your message. Messages from the tool and blocks "printed by the program" appear.
- The sheet can come back in the middle of the chat if the chatbot suggests new facts.

## Rules

- You only know what is on your screen and in persona.md. Do NOT open anything else in the run folder (not `program/`,
  `model/`, `inputs.json`, `model.jsonl`, `status.json`, `screen_full.txt`), not the repository, not the web. Your
  character does not know Florida law.
- `my_lease.txt` is your lease. Like most students you have never really read it. Open it only if the tool tells you to
  check something in it, or if your character would plausibly look (say so in your notes).
- Stay in character when typing. Be realistic: short or messy messages, the questions a real student would ask, push
  back when an answer is confusing ("wait so can i or can't i?"). Do not try to test the tool like an engineer.
- In the chat, send about 4 to 6 messages in all, following what you actually want and what the answers make you
  wonder. When you are done, type `bye`.
- Keep a diary: after each screen you read, append to `RUN/notes.md` a few honest lines: what you understood, what
  confused you, how you felt, what you'd do right now in real life. Quote the screen where it matters.

## At the end (after `bye` and DONE, or if the program stops on its own)

Write `RUN/evaluation.md`, in your character's voice first, then a short plain summary:

1. In one sentence: did this help me?
2. What I came for vs. what I got.
3. Ease of use: the intake questions, the length and wording of the replies, the program-printed blocks.
4. Trust: did I believe it? did I feel safe acting on it? why?
5. What I am going to do now, concretely (and whether the tool is why).
6. Moments of confusion, quoting the screen.
7. What I expected and did not get (about roommates, the management company, amenities, money back, etc.).
8. Ratings 1-5 with one line each: Usefulness, Clarity, Trust, Ease of use, Would recommend to a friend.
9. The one change that would make me use it again.
