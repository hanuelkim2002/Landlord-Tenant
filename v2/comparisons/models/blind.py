"""Makes the blind ranking for test 1: each story's four first-run answers under W, X, Y, Z, shuffled per story. Writes
answers.json, key.json (which letter is which model; not shown until ranked), page.html, and a ranks.json to fill in.
Run from this folder: python blind.py sample   (or own; add --dry to use the made-up --dry results)
"""
import argparse
import html
import json
import random
import re

import models

LETTERS = ["W", "X", "Y", "Z"]


def plain(answer):
    """The answer as plain text for the page: markdown bold and headings marks taken off, nothing else changed."""
    return re.sub(r"^#+\s*", "", answer.replace("**", ""), flags=re.M).strip()


def first_runs(folder):
    """Each model's run-1 answers, as {model: {story id: answer}}."""
    found = {}
    for model in models.CHAT_MODELS:
        lines = models.read_lines(folder / f"stories_{model}.jsonl")
        found[model] = {line["story"]: line["answer"] for line in lines if line["run"] == 1}
    return found


def shuffled(stories, answers):
    """For each story, the four answers under shuffled letters, and the key to the letters."""
    rng = random.Random(20261019)                             # the same shuffle if the page is made again
    page, key = [], {}
    for story in stories:
        order = list(models.CHAT_MODELS)
        rng.shuffle(order)
        key[story["id"]] = dict(zip(LETTERS, order))
        page.append({"id": story["id"], "title": story["title"], "message": story["message"], "key": story["answer"],
                     "answers": {letter: plain(answers[m][story["id"]]) for letter, m in zip(LETTERS, order)}})
    return page, key


def card(story_number, letter, text):
    """One answer, with its letter and a rank to choose."""
    options = "".join(f"<option value='{n}'>{n}</option>" for n in ("", 1, 2, 3, 4))
    return (f"<div style='background:var(--surface-2,#f4f4f1);border:0.5px solid var(--border,#ccc);border-radius:12px;padding:12px 14px;'>"
            f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>"
            f"<span style='font-weight:500;font-size:15px;'>Answer {letter}</span>"
            f"<label style='font-size:13px;color:var(--text-secondary,#555);'>Rank "
            f"<select data-story='{story_number}' data-letter='{letter}' style='width:64px;'>{options}</select></label></div>"
            f"<div style='font-size:13px;line-height:1.6;white-space:pre-wrap;color:var(--text-primary,#111);'>{html.escape(text)}</div></div>")


def page_html(page):
    """The side-by-side page: each story with the tenant's message on top, its four answers in a grid, a rank for each,
    and a button that sends the ranks (or, outside the chat, shows them to copy)."""
    parts = [f"<h2 class='sr-only'>Blind ranking of four answers to each of {len(page)} stories.</h2>"]
    for n, story in enumerate(page, start=1):
        parts.append(
            f"<div style='margin:1.5rem 0 0.5rem;'><h3 style='margin:0 0 6px;'>Story {n}: {html.escape(story['title'])}</h3>"
            f"<div style='font-size:14px;color:var(--text-secondary,#555);margin-bottom:6px;'>The tenant: {html.escape(story['message'])}</div>"
            f"<details style='font-size:13px;color:var(--text-secondary,#555);margin-bottom:10px;'><summary>The answer key</summary>"
            f"<div style='margin-top:6px;'>{html.escape(story['key'])}</div></details>"
            f"<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;'>"
            + "".join(card(n, letter, story["answers"][letter]) for letter in LETTERS) +
            f"</div><textarea data-note='{n}' placeholder='A note on story {n} (optional)' "
            f"style='width:100%;margin-top:8px;min-height:40px;font-size:13px;'></textarea></div>")
    parts.append("<div style='margin:1.5rem 0;display:flex;align-items:center;gap:12px;'>"
                 "<button id='send'>Send my rankings</button>"
                 "<span id='error' style='font-size:13px;color:var(--text-danger,#b00);'></span></div>"
                 "<pre id='copy' style='white-space:pre-wrap;font-size:13px;'></pre>")
    parts.append("""<script>
document.getElementById('send').addEventListener('click', () => {
  const lines = [];
  for (let n = 1; n <= %d; n++) {
    const ranks = [...document.querySelectorAll(`select[data-story="${n}"]`)].map(s => `${s.dataset.letter}=${s.value}`);
    if (ranks.some(r => r.endsWith('='))) {
      document.getElementById('error').textContent = `Rank every answer first (story ${n} is missing one).`;
      return;
    }
    const note = document.querySelector(`textarea[data-note="${n}"]`).value.trim();
    lines.push(`Story ${n}: ${ranks.join(', ')}${note ? ' (note: ' + note + ')' : ''}`);
  }
  document.getElementById('error').textContent = '';
  const text = 'My blind rankings (1 is best):\\n' + lines.join('\\n');
  if (typeof sendPrompt === 'function') { sendPrompt(text); } else { document.getElementById('copy').textContent = text; }
});
document.querySelectorAll('select').forEach(s => s.addEventListener('change', () => document.getElementById('error').textContent = ''));
</script>""" % len(page))
    return "\n".join(parts)


def main():
    """Make the blind files from the first-run answers."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("lease_set", choices=["sample", "own"])
    parser.add_argument("--dry", action="store_true", help="use the made-up --dry results")
    args = parser.parse_args()
    own = args.lease_set == "own"
    if own and models.missing([models.PRIVATE / "own_stories.json"]):
        print("Cannot run yet. private/own_stories.json is missing.")
        return
    stories = models.stories(own)["stories"]
    answers = first_runs(models.results_folder(own, args.dry))
    lacking = [m for m in models.CHAT_MODELS if any(s["id"] not in answers[m] for s in stories)]
    if lacking:
        print(f"Cannot run yet. These models have no run-1 answer to every story: {', '.join(lacking)}")
        return
    page, key = shuffled(stories, answers)
    out = models.blind_folder(own, args.dry)
    out.mkdir(parents=True, exist_ok=True)
    (out / "answers.json").write_text(json.dumps(page, indent=1))
    (out / "key.json").write_text(json.dumps(key, indent=1))
    (out / "page.html").write_text(page_html(page))
    if not (out / "ranks.json").exists():                     # never overwrite ranks the author has filled in
        template = {"ranks_by_letter": {s["id"]: {letter: None for letter in LETTERS} for s in stories}, "notes": {}}
        (out / "ranks.json").write_text(json.dumps(template, indent=1))
    print(f"blind page written to {out}: {sum(len(s['answers']) for s in page)} answers")


if __name__ == "__main__":
    main()
