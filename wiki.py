"""Case wiki: the linked markdown pages in wiki/ (README, The unit of legal knowledge) and the code checks that
keep them honest. Claude Code writes the pages from cases/ and statutes/ in development sessions, following
wiki/SCHEMA.md; the author reads each page and signs off; tenant sessions will only read verified pages.
Nothing here calls a model.

    python wiki.py check                       # every check: problems (to fix) and warnings (to look at)
    python wiki.py index                       # rewrite wiki/index.md from the pages
    python wiki.py verify "<page>" "<name>"    # the author signs off on a page after reading it

A page is a markdown file in wiki/cases/ or wiki/topics/, named for what it is about ("Durene v. Alcime.md"),
with YAML front matter between two "---" lines. Pages link to each other with [[Page name]], as Obsidian does.
"""
import hashlib
import re
import sys
from datetime import date

import yaml

from citations import compact, is_in, where_in
from config import CASES, WIKI
from corpus import statute

# The court's and the statute's words appear on a page only as a quote followed by its source:
#   "words" (at 1210)                         this case page's own opinion, starting on page 1210
#   "words" ([[Plakhov v. Serova]] at 1223)   another case page's opinion
#   "words" (Fla. Stat. 83.49(3)(a))          the stored statute
QUOTE = re.compile(r'"([^"\n]+)" \((?:at (\d+)|\[\[([^\]]+)\]\] at (\d+)|Fla\. Stat\. (83\.\d+(?:\([0-9a-z]+\))*))\)')
QUOTE_MARKS = re.compile(r'"[^"\n]{20,}"')      # any double-quoted passage; each must be a QUOTE with its source
LINK = re.compile(r"\[\[([^\]|#]+)")            # [[Page name]], [[Page name|shown text]]
STAR = re.compile(r"\*(\d+)")                   # a star page in an opinion: "*1210" starts page 1210
REQUIRED = {"case": ["cite", "file", "court", "decided", "statute_read", "sections", "topics"],
            "topic": []}
SIGN_OFF = ("verified_by:", "verified_on:", "verified_hash:")   # set by verify, left out of the page's hash


def read_pages(root=WIKI):
    """Every page under root/cases and root/topics, by name: {"name", "path", "meta", "body"}."""
    pages = {}
    for path in sorted(root.glob("cases/*.md")) + sorted(root.glob("topics/*.md")):
        _, front, body = path.read_text().split("---\n", 2)
        pages[path.stem] = {"name": path.stem, "path": path, "meta": yaml.safe_load(front) or {}, "body": body}
    return pages


def linked(value):
    """The page names in a front matter field: '[[Durene v. Alcime]]', or a list of them."""
    items = value if isinstance(value, list) else [value] if value else []
    return [LINK.search(str(item)).group(1).strip() for item in items if LINK.search(str(item))]


def page_hash(path):
    """A fingerprint of the page as the author read it, without its sign-off lines (so signing changes
    nothing). Any later edit changes it."""
    kept = [line for line in path.read_text().split("\n") if not line.startswith(SIGN_OFF)]
    return hashlib.sha256("\n".join(kept).encode()).hexdigest()[:16]


def verified(page):
    """True if the author signed off on the page and it has not changed since."""
    return bool(page["meta"].get("verified_by")) and page["meta"].get("verified_hash") == page_hash(page["path"])


def opinion(page):
    """A case page's opinion from cases/: its text with the star pages taken out (so a quote can run across a
    page break), and where each page starts, as [(position in the compact text, page)]. A star outside the
    opinion's own page range is the court's (a Westlaw cite's "at *3") and stays in the text."""
    first = int(str(page["meta"]["cite"]).split()[-1])
    text = (CASES / page["meta"]["file"]).read_text()
    plain, starts, last = "", [(0, first)], 0
    for m in STAR.finditer(text):
        if first < int(m.group(1)) < first + 200:
            plain += text[last:m.start()]
            starts.append((len(compact(plain)), int(m.group(1))))
            last = m.end()
    return plain + text[last:], starts


def pin(quote, plain, starts):
    """The page a quote starts on: the last page started before the quote's first words."""
    first_piece = next(p.strip(" .,;:") for p in re.split(r"\.\.\.|…", quote) if p.strip(" .,;:"))
    at = compact(plain).find(compact(first_piece))
    return max(page for position, page in starts if position <= at)


def case_list(topic):
    """The "## Cases" section of a topic page, up to the next heading. A link elsewhere on the page (a quote's
    source) does not count as listing the case."""
    after = topic["body"].partition("\n## Cases\n")[2]
    return after.split("\n## ")[0]


def short(words):
    """The first six words of a quote, to name it in a message."""
    return " ".join(words.split()[:6]) + ("..." if len(words.split()) > 6 else "")


def check_quotes(page, pages, opinions):
    """Every quote on a page is word for word in its source and starts on the page it cites; no quote is
    left without a source. Returns problem lines."""
    name, body, problems = page["name"], page["body"], []
    sourced = {m.start() for m in QUOTE.finditer(body)}
    for m in QUOTE_MARKS.finditer(body):
        if m.start() not in sourced:
            problems.append(f"{name}: a quote with no source: {short(m.group())}")
    for m in QUOTE.finditer(body):
        words, own_pin, other, other_pin, cite = m.groups()
        if cite:                                                      # the statute
            section = cite.split("(")[0]
            where = where_in(words, section) if section in statute else None
            if where is None:
                problems.append(f'{name}: "{short(words)}" is not in Fla. Stat. {section}')
            elif not where.startswith(cite):
                problems.append(f'{name}: "{short(words)}" is in {where}, not {cite}')
            continue
        source = page if own_pin else pages.get(other.strip())
        if own_pin and page["meta"].get("kind") != "case":
            problems.append(f'{name}: "{short(words)}" says (at {own_pin}) on a topic page; name the case')
            continue
        if source is None or source["meta"].get("kind") != "case":
            problems.append(f"{name}: quotes [[{other}]], which is not a case page")
            continue
        if source["name"] not in opinions:
            opinions[source["name"]] = opinion(source)
        plain, starts = opinions[source["name"]]
        claimed = int(own_pin or other_pin)
        if not is_in(words, plain):
            problems.append(f'{name}: "{short(words)}" is not in {source["meta"]["cite"]}')
        elif pin(words, plain, starts) != claimed:
            problems.append(f'{name}: "{short(words)}" starts at {pin(words, plain, starts)}, not {claimed}')
    return problems


def lint(root=WIKI):
    """Every check on the wiki under root. Returns (problems, warnings), each a list of lines that start with
    the page's name. Problems must be fixed; warnings are for the author to look at."""
    pages = read_pages(root)
    problems, warnings, opinions = [], [], {}
    for name, page in pages.items():
        meta, kind = page["meta"], page["meta"].get("kind")
        if kind not in REQUIRED or page["path"].parent.name != kind + "s":
            problems.append(f"{name}: kind is {kind!r}; a page in cases/ is a case and one in topics/ a topic")
            continue
        for field in REQUIRED[kind] + ["sections"] + [key.rstrip(":") for key in SIGN_OFF]:
            if field not in meta or (meta[field] in (None, "", []) and field in REQUIRED[kind]):
                problems.append(f"{name}: front matter has no {field}")
        for section in meta.get("sections") or []:
            if section not in statute:
                problems.append(f"{name}: tagged {section}, which is not in statutes/")
        for target in LINK.findall(page["path"].read_text()):
            if target.strip() not in pages:
                problems.append(f"{name}: link [[{target}]] goes to no page")
        problems += check_quotes(page, pages, opinions)
        if meta.get("verified_by") and not verified(page):
            warnings.append(f"{name}: changed since {meta['verified_by']} verified it on {meta.get('verified_on')}; "
                            f"read it and verify it again")
        if kind != "case" or not (CASES / str(meta.get("file"))).exists():
            if kind == "case":
                problems.append(f"{name}: no file cases/{meta.get('file')}")
            continue
        first_line = (CASES / meta["file"]).read_text().split("\n")[0].removesuffix(" (Mem)")
        if re.sub(r"[^0-9A-Za-z]", "", first_line) != re.sub(r"[^0-9A-Za-z]", "", str(meta["cite"])):
            problems.append(f"{name}: cite {meta['cite']} is not the cite of cases/{meta['file']} ({first_line})")
        for label in ("Rule:", "Reasoning:"):
            if label not in page["body"]:
                problems.append(f"{name}: no {label} line")
        for topic in linked(meta.get("topics")):
            if topic in pages and f"[[{name}]]" not in case_list(pages[topic]):
                problems.append(f"{name}: names topic [[{topic}]], whose Cases list does not have it")
        plain = opinion(page)[0]
        for section in meta.get("sections") or []:
            if not re.search(re.escape(section) + r"(?!\d)", plain):
                warnings.append(f"{name}: tagged {section}, which the opinion never cites")
    index = root / "index.md"
    if not index.exists() or index.read_text() != render_index(pages):
        problems.append("index.md: out of date; run python wiki.py index")
    return problems, warnings


def render_index(pages):
    """wiki/index.md: the pages by statute section, the topics with the cases that name them, and every case.
    Built from the pages; never edited by hand."""
    cases = {n: p for n, p in pages.items() if p["meta"].get("kind") == "case"}
    topics = {n: p for n, p in pages.items() if p["meta"].get("kind") == "topic"}
    tagged = lambda group, section: [f"[[{n}]]" for n, p in group.items() if section in (p["meta"].get("sections") or [])]
    lines = ["# Index", "", "Built by `python wiki.py index` from the pages. Do not edit by hand.", "",
             "## By statute section", ""]
    for section in sorted({s for p in pages.values() for s in p["meta"].get("sections") or []}, key=float):
        lines += [f"### {section}", "", "Topics: " + (", ".join(tagged(topics, section)) or "none"),
                  "", "Cases: " + (", ".join(tagged(cases, section)) or "none"), ""]
    untagged = [f"[[{n}]]" for n, p in topics.items() if not p["meta"].get("sections")]
    if untagged:
        lines += ["### No section", "", "Topics: " + ", ".join(untagged), ""]
    lines += ["## Topics", ""]
    for n in topics:
        named_by = [f"[[{c}]]" for c, p in cases.items() if n in linked(p["meta"].get("topics"))]
        lines.append(f"- [[{n}]]: " + (", ".join(named_by) or "no case yet"))
    lines += ["", "## Cases", "", "| Case | Cite | Court | Decided | Sections | Verified |", "|---|---|---|---|---|---|"]
    for n, p in cases.items():
        m = p["meta"]
        lines.append(f"| [[{n}]] | {m.get('cite')} | {m.get('court')} | {m.get('decided')} | "
                     f"{', '.join(m.get('sections') or [])} | {'yes' if verified(p) else 'no'} |")
    return "\n".join(lines) + "\n"


def write_index(root=WIKI):
    (root / "index.md").write_text(render_index(read_pages(root)))


def verify(name, by, root=WIKI):
    """The author's sign-off on a page they have read against its sources: sets verified_by, verified_on
    (today), and verified_hash (the page as read), then rewrites the index. Refused while the page has a
    problem. A later edit changes the page's hash, which undoes the sign-off until it is verified again."""
    pages = read_pages(root)
    if name not in pages:
        raise ValueError(f"no page named {name}")
    own = [p for p in lint(root)[0] if p.startswith(name + ":")]
    if own:
        raise ValueError("fix these first:\n" + "\n".join(own))
    path = pages[name]["path"]
    stamp = {"verified_by:": f"verified_by: {by}", "verified_on:": f"verified_on: {date.today()}",
             "verified_hash:": f"verified_hash: {page_hash(path)}"}
    lines = [stamp[line.split(":")[0] + ":"] if line.startswith(SIGN_OFF) else line
             for line in path.read_text().split("\n")]
    path.write_text("\n".join(lines))
    write_index(root)


def check_wiki(root=WIKI):
    """Print every problem and warning, then a count. Like the playbook checks: no problem may remain."""
    problems, warnings = lint(root)
    for line in problems:
        print("FAIL " + line)
    for line in warnings:
        print("WARN " + line)
    print(f"{len(read_pages(root))} pages: {len(problems)} problems, {len(warnings)} warnings")
    return problems


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "check"
    if command == "index":
        write_index()
        print(f"wrote {WIKI / 'index.md'}")
    elif command == "verify":
        verify(sys.argv[2], sys.argv[3])
        print(f"verified {sys.argv[2]}")
    else:
        check_wiki()
