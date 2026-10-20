"""Makes the blind ranking: for each story, the four methods' first-run answers under the letters W, X, Y, Z, in an
order shuffled per story. Writes blind/answers.json (what the author sees), blind/key.json (which letter is which
method, not shown until the author has ranked), and blind/page.html (the side-by-side page).
Run from this folder: python blind.py
"""
import html
import json
import random
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
METHODS = ["v1", "A", "B", "C"]
LETTERS = ["W", "X", "Y", "Z"]


def plain(answer):
    """The answer as plain text for the page: markdown bold and headings marks taken off, nothing else changed."""
    return re.sub(r"^#+\s*", "", answer.replace("**", ""), flags=re.M).strip()


def shuffled():
    """For each story, the four first-run answers under shuffled letters, and the key to the letters."""
    stories = json.loads((HERE / "stories.json").read_text())["stories"]
    answers = {m: {json.loads(l)["story"]: json.loads(l) for l in (HERE / "results" / f"{m}.jsonl").read_text().splitlines()
                   if json.loads(l)["run"] == 1} for m in METHODS}
    rng = random.Random(20261019)                            # the same shuffle if the page is made again
    page, key = [], {}
    for story in stories:
        order = METHODS[:]
        rng.shuffle(order)
        key[story["id"]] = dict(zip(LETTERS, order))
        page.append({"id": story["id"], "title": story["title"], "message": story["message"], "key": story["answer"],
                     "answers": {letter: plain(answers[m][story["id"]]["answer"]) for letter, m in zip(LETTERS, order)}})
    return page, key


def card(story_number, letter, text):
    """One answer, with its letter and a rank to choose."""
    options = "".join(f"<option value='{n}'>{n}</option>" for n in ("", 1, 2, 3, 4))
    return (f"<div style='background:var(--surface-2);border:0.5px solid var(--border);border-radius:12px;padding:12px 14px;'>"
            f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>"
            f"<span style='font-weight:500;font-size:15px;'>Answer {letter}</span>"
            f"<label style='font-size:13px;color:var(--text-secondary);'>Rank "
            f"<select data-story='{story_number}' data-letter='{letter}' style='width:64px;'>{options}</select></label></div>"
            f"<div style='font-size:13px;line-height:1.6;white-space:pre-wrap;color:var(--text-primary);'>{html.escape(text)}</div></div>")


def page_html(page):
    """The side-by-side page: each story, its four answers in a grid, a rank for each, and a button that sends the ranks."""
    parts = ["<h2 class='sr-only'>Blind ranking of four answers to each of five deposit stories.</h2>"]
    for n, story in enumerate(page, start=1):
        parts.append(
            f"<div style='margin:1.5rem 0 0.5rem;'><h3 style='margin:0 0 6px;'>Story {n}: {html.escape(story['title'].lower().capitalize())}</h3>"
            f"<div style='font-size:14px;color:var(--text-secondary);margin-bottom:6px;'>The tenant: {html.escape(story['message'])}</div>"
            f"<details style='font-size:13px;color:var(--text-secondary);margin-bottom:10px;'><summary>The answer key</summary>"
            f"<div style='margin-top:6px;'>{html.escape(story['key'])}</div></details>"
            f"<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;'>"
            + "".join(card(n, letter, story["answers"][letter]) for letter in LETTERS) +
            f"</div><textarea data-note='{n}' placeholder='A note on story {n} (optional)' "
            f"style='width:100%;margin-top:8px;min-height:40px;font-size:13px;'></textarea></div>")
    parts.append("<div style='margin:1.5rem 0;display:flex;align-items:center;gap:12px;'>"
                 "<button id='send'>Send my rankings ↗</button>"
                 "<span id='error' style='font-size:13px;color:var(--text-danger);'></span></div>")
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
  sendPrompt('My blind rankings (1 is best):\\n' + lines.join('\\n'));
});
document.querySelectorAll('select').forEach(s => s.addEventListener('change', () => document.getElementById('error').textContent = ''));
</script>""" % len(page))
    return "\n".join(parts)


if __name__ == "__main__":
    page, key = shuffled()
    out = HERE / "blind"
    out.mkdir(exist_ok=True)
    (out / "answers.json").write_text(json.dumps(page, indent=1))
    (out / "key.json").write_text(json.dumps(key, indent=1))
    (out / "page.html").write_text(page_html(page))
    print("blind page written:", sum(len(s["answers"]) for s in page), "answers")
