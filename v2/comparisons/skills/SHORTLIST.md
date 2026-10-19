# Skills: the shortlist

What is tested is the **body** of a skill, the part the model reads after it loads the skill. Every method gets the same
container: a short header with the skill's name and a one-line description, which is all the model sees before it
loads a skill (Anthropic's Agent Skills design, [Anthropic][skills]). Every method also carries the same legal
content: v1's `deposit_not_returned` and the sections of `statutes/` it rests on (83.49 and 83.505). Only the way it
is written differs, so the method is the only difference. v1's own skill runs beside them as the baseline.

## A. An element checklist

For each thing the tenant may be able to do, the conditions it needs, in order, each one sentence with the statute's
words quoted and cited, and a line saying how to combine them ("all three must be met"). The model settles each
condition from the facts (met, not met, the tenant can tell us, not settled) and then answers.

- Why it is promising: this is how a lawyer applies a rule with several elements, and a prompt built this way
  ("Chain of Logic": solve each element, then combine them) beat chain-of-thought and other prompting on legal rules
  with several elements, with open and commercial models ([Servantez et al. 2024][col]). It is short, and each
  quote sits beside the one condition it supports, so it is easy to check.
- The risk: it says how to apply a rule, not what a good answer sounds like, so the answer may come out as a list of
  conditions instead of an answer (the "too rigid" problem of v1).

## B. Worked examples

A short statement of the rule (the same conditions, in a paragraph), then two or three example stories, each with a
model answer: the answer first, the conditions applied to that story's facts, the cites, the one question it needs.
The examples use facts unlike the test stories.

- Why it is promising: examples teach the shape of a good answer directly, which the checklist does not. Applying a
  rule to example fact patterns is how the LegalBench rule tasks prompt models ([Servantez et al. 2024][col]).
- The risk: studies of prompting with examples find that models pick up what is on the surface of the examples
  (their wording, their outcome) more than the rule underneath, and that merely reordering the examples moves the
  results ([Order Matters, 2025][order]). Examples also make the skill longer.

## C. A short core, with the details in a file read only when needed

The Agent Skills way: the skill's body holds only the core (when it applies, each option and its conditions in a line,
the deadlines in plain words: which fact, how many days). The statute's words, the open questions with their readings
on each side, and the mistakes to avoid sit in a second file the model opens with a tool when it needs them
([Anthropic][skills]).

- Why it is promising: the prompt stays short, which matters because models do worse as the prompt grows ([Chroma
  2025][rot]), and v2's prompt already carries the whole lease.
- The risk: the model may not open the details when it should, as method B of the lease test kept reading instead of
  answering. An open question or a statute's exact words may be skipped.

## Baseline: v1's skill, as it is

`v1/skills/deposit_not_returned.md`, 3,030 words, unchanged, loaded the same way. Its deadline clocks and
`get_deadlines` are v1's code, which v2 leaves out, so its "Deadlines" part tells the model to call a tool that
does not exist in the test. The test gives every method `count_days` instead, and v1's skill still reads as written.

## Left off the list, and why

- **A decision tree** (questions in order, leading to outcomes). Studies of decision trees placed whole in a prompt
  find the model loses its place in them, and the fixes run the tree in code and ask the model one step at a time
  ([FloCA 2026][floca]). That is what v1's options layer did, and the author found it too rigid. As prose in a
  prompt, a deposit tree also branches fast (early move-out, month-to-month, a notice by text).

## Also to know

A study of statutory reasoning found a model did well on statutes it had seen in training and poorly on simple new
ones it had not ([Blair-Stanek et al. 2023][sara]). So the test checks that the model applies the skill's quoted words,
not what it remembers about deposits.

[skills]: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
[col]: https://arxiv.org/abs/2402.10400
[order]: https://arxiv.org/html/2511.09700v1
[rot]: https://trychroma.com/research/context-rot
[floca]: https://arxiv.org/abs/2602.14035
[sara]: https://arxiv.org/pdf/2302.06100
