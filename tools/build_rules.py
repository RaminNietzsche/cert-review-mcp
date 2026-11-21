#!/usr/bin/env python3
"""Parse the CMU SEI secure-coding-standards content tree into data/rules.json.

Usage:
    python3 tools/build_rules.py --src /workspace/cert-src [--out data/rules.json]

The source checkout is pinned: its git commit is recorded in the output and in
NOTICE. Official rule counts are taken from the standard's own index pages and
compared with what was parsed; any discrepancy is written to the report and
makes the script exit non-zero (use --allow-mismatch to only warn).
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path

BASE_URL = "https://cmu-sei.github.io/secure-coding-standards"
STANDARDS = {
    "c": {
        "dir": "4.sei-cert-c-coding-standard",
        "slug": "sei-cert-c-coding-standard",
        "name": "SEI CERT C Coding Standard",
        "suffix": "C",
        "parts": [("rule", "03.rules", "03.rules/01.index.md"),
                  ("recommendation", "08.recommendations",
                   "08.recommendations/01.index.md")],
    },
    "cpp": {
        "dir": "5.sei-cert-cpp-coding-standard",
        "slug": "sei-cert-cpp-coding-standard",
        "name": "SEI CERT C++ Coding Standard",
        "suffix": "CPP",
        "parts": [("rule", "3.rules", "3.rules/01.index.md")],
    },
}
ID_RE = re.compile(r"^[A-Z]{3}\d{2}-(?:C|CPP)$")
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
CODE_RE = re.compile(
    r"::code-block(?:\{([^}]*)\})?\n```[ \t]*([^\n]*)\n(.*?)\n```\n?::", re.S)
TITLE_RE = re.compile(r"^#\s+([A-Z]{3}\d{2}-(?:C|CPP))\.\s*(.+?)\s*$", re.M)
LINK_ID_RE = re.compile(
    r"\[([A-Z]{3}\d{2}-(?:C|CPP))\.(?:\\.|[^\]\\])*\]\(([^)]+)\)")


REL_LINK_RE = re.compile(r"\[((?:\\.|[^\]\\])+)\]\(/[^)]*\)")


def strip_html(s: str) -> str:
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).replace("**", "").strip()


def clean_inline(s: str) -> str:
    s = REL_LINK_RE.sub(lambda m: m.group(1).strip(), s)
    return re.sub(r"\s+", " ", strip_html(s)).strip()


def parse_front_matter(text: str):
    m = FM_RE.match(text)
    tags: list[str] = []
    if m:
        for line in m.group(1).splitlines():
            line = line.strip()
            if line.startswith("- "):
                tags.append(line[2:].strip())
        text = text[m.end():]
    return tags, text


def split_sections(body: str):
    """Return (intro, [(heading, text)]) splitting on level-2 headings."""
    parts = re.split(r"^## (.+?)\s*$", body, flags=re.M)
    intro = parts[0]
    secs = [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]
    return intro, secs


def parse_code_blocks(text: str):
    blocks = []
    for m in CODE_RE.finditer(text):
        attrs = m.group(1) or ""
        q = re.search(r'quality="(\w+)"', attrs)
        blocks.append({
            "quality": q.group(1) if q else None,
            "lang": (m.group(2) or "").strip() or None,
            "code": m.group(3),
        })
    return blocks


def md_clean(text: str) -> str:
    """Reduce links into the standard's own site to their text."""
    text = REL_LINK_RE.sub(lambda m: m.group(1).strip(), text)
    return re.sub(r"[ \t]+\n", "\n", text).strip()


def prose_of(text: str) -> str:
    return md_clean(CODE_RE.sub("[code]", text))


def parse_html_table(text: str):
    trs = re.findall(r"<tr[^>]*>(.*?)</tr>", text, flags=re.S)
    parsed = [[c for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, flags=re.S)]
              for tr in trs]
    parsed = [r for r in parsed if r]
    if len(parsed) < 2:
        return None, []
    return [clean_inline(c) for c in parsed[0]], parsed[1:]


def parse_table(text: str):
    """Parse the first markdown pipe (or HTML) table -> (header, rows)."""
    if "<table" in text and "<tr" in text:
        return parse_html_table(text)
    header, rows = None, []
    for line in text.splitlines():
        s = line.strip()
        if s.count("|") < 2 or not s:
            continue
        cells = s.strip("|").split("|")
        if all(re.fullmatch(r"\s*:?-{3,}:?\s*", c) for c in cells):
            continue
        if header is None:
            h = [clean_inline(c) for c in cells]
            if not any(h):          # some pages start with an empty header row
                continue
            header = h
            continue
        rows.append(cells)
    return header, rows


def parse_risk(sec_text: str, rule_id: str):
    header, rows = parse_table(sec_text)
    if not header:
        return None
    for cells in rows:
        vals = [clean_inline(c) for c in cells]
        if vals and vals[0].upper() == rule_id.upper():
            d = {}
            for h, v in zip(header[1:], vals[1:]):
                key = h.lower().replace(" ", "_")
                d[key] = v
            return d
    return None


def parse_detection(sec_text: str):
    header, rows = parse_table(sec_text)
    out = []
    if not header:
        return out
    for cells in rows:
        if len(cells) < 4:
            continue
        tool = clean_inline(cells[0])
        out.append({
            "tool": tool,
            "version": clean_inline(cells[1]),
            "checker": [c.strip() for c in strip_html(cells[2]).split("\n")
                        if c.strip()],
            "description": clean_inline(cells[3]),
        })
    return out


def parse_related(sec_text: str):
    header, rows = parse_table(sec_text)
    out = []
    if not header:
        return out
    for cells in rows:
        vals = [clean_inline(c) for c in cells]
        if len(vals) >= 2:
            out.append({"taxonomy": vals[0], "item": vals[1],
                        "relationship": vals[2] if len(vals) > 2 else ""})
    return out


def pair_examples(sections):
    """Pair noncompliant examples with the compliant solutions that follow."""
    pairs, cur = [], None
    for heading, text in sections:
        low = heading.lower()
        if low.startswith("noncompliant code example"):
            cur = {"noncompliant": {"heading": heading,
                                    "text": prose_of(text),
                                    "code": parse_code_blocks(text)},
                   "compliant": []}
            pairs.append(cur)
        elif low.startswith("compliant solution"):
            item = {"heading": heading, "text": prose_of(text),
                    "code": parse_code_blocks(text)}
            if cur is None:
                cur = {"noncompliant": None, "compliant": []}
                pairs.append(cur)
            cur["compliant"].append(item)
    return pairs


def git_head(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()


def git_date(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "log", "-1", "--format=%cI"], text=True).strip()


def url_for(std, kind, rel_dir_slug, file_stem):
    folder = "rules" if kind == "rule" else "recommendations"
    return f"{BASE_URL}/{std['slug']}/{folder}/{rel_dir_slug}/{file_stem}"


def strip_num(name: str) -> str:
    return re.sub(r"^\d+\.", "", name)


def parse_rule_file(path: Path, std, lang, kind, category_dir):
    text = path.read_text(encoding="utf-8")
    tags, body = parse_front_matter(text)
    m = TITLE_RE.search(body)
    if not m:
        return None
    rid, title = m.group(1), m.group(2)
    body_after = body[m.end():]
    intro, secs = split_sections(body_after)
    sec = {h: t for h, t in secs}
    cat_slug = strip_num(category_dir)
    cat_code = cat_slug.rsplit("-", 1)[-1].upper()
    rec = {
        "id": rid, "lang": lang, "kind": kind,
        "category": cat_code, "category_name": strip_html(
            re.sub(r"-[a-z]{3}$", "", cat_slug).replace("-", " ").title()),
        "title": title,
        "tags": [t for t in tags if not t.startswith("cwe-")],
        "cwe": sorted({t.upper() for t in tags if t.startswith("cwe-")}),
        "url": url_for(STANDARDS[lang], kind, cat_slug,
                       strip_num(path.stem).lower()),
        "source_path": str(path.relative_to(path.parents[
            len(path.relative_to(path.parents[-1]).parts) - 2]))
        if False else None,
        "intro": md_clean(intro),
        "examples": pair_examples(secs),
        "exceptions": prose_of(sec.get("Exceptions", "")) or None,
        "risk": None, "automated_detection": [], "related_guidelines": [],
        "risk_text": "", "sections": [h for h, _ in secs],
    }
    for h, t in secs:
        if h.startswith("Risk Assessment"):
            rec["risk_text"] = prose_of(t.split("\n|")[0])
            r = parse_risk(t, rid)
            if r:
                rec["risk"] = normalize_risk(r)
        elif h == "Automated Detection":
            rec["automated_detection"] = parse_detection(t)
        elif h == "Related Guidelines":
            rec["related_guidelines"] = parse_related(t)
    return rec


def normalize_risk(r: dict) -> dict:
    out = {"severity": r.get("severity"), "likelihood": r.get("likelihood"),
           "detectable": r.get("detectable"), "repairable": r.get("repairable"),
           "remediation_cost": r.get("remediation_cost"),
           "priority": r.get("priority"), "level": r.get("level")}
    for k in ("detectable", "repairable"):
        if out[k] is not None:
            out[k] = out[k].strip().lower() == "yes"
    return {k: v for k, v in out.items() if v is not None}


def official_ids(index_path: Path, std, kind):
    """IDs listed on an index page that belong to this standard and kind.

    Index pages also cross-link rules of the other standard and the other
    kind, so only links under /<slug>/<rules|recommendations>/ count.
    """
    folder = "rules" if kind == "rule" else "recommendations"
    want = f"/{std['slug']}/{folder}/"
    ids = {}
    for m in LINK_ID_RE.finditer(index_path.read_text(encoding="utf-8")):
        if want in m.group(2):
            ids[m.group(1)] = m.group(2)
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, type=Path)
    ap.add_argument("--out", default="data/rules.json", type=Path)
    ap.add_argument("--report", default="docs/rule-counts.md", type=Path)
    ap.add_argument("--allow-mismatch", action="store_true")
    a = ap.parse_args()
    content = a.src / "content"
    commit, cdate = git_head(a.src), git_date(a.src)

    rules, report, mismatch = [], [], False
    for lang, std in STANDARDS.items():
        root = content / std["dir"]
        for kind, sub, idx in std["parts"]:
            parsed = {}
            for cat in sorted((root / sub).iterdir()):
                if not cat.is_dir():
                    continue
                for f in sorted(cat.glob("*.md")):
                    rec = parse_rule_file(f, std, lang, kind, cat.name)
                    if rec and ID_RE.match(rec["id"]):
                        if rec["id"] in parsed:
                            print(f"duplicate id {rec['id']}", file=sys.stderr)
                        parsed[rec["id"]] = rec
            # Official listing: master index plus per-category indexes.
            off = official_ids(root / idx, std, kind)
            for cat in sorted((root / sub).iterdir()):
                ci = cat / ("01.index.md" if (cat / "01.index.md").exists()
                            else "1.index.md")
                if ci.exists():
                    off.update(official_ids(ci, std, kind))
            # Keep only ids of this kind (index pages of other kinds excluded).
            only_parsed = sorted(set(parsed) - set(off))
            only_off = sorted(set(off) - set(parsed))
            line = (f"| {std['name']} | {kind}s | {len(off)} | {len(parsed)} | "
                    f"{', '.join(only_off) or '-'} | "
                    f"{', '.join(only_parsed) or '-'} |")
            report.append(line)
            if only_off or only_parsed:
                mismatch = True
            rules.extend(parsed.values())

    rules.sort(key=lambda r: (r["lang"], r["kind"], r["id"]))
    for r in rules:
        r.pop("source_path", None)
    out = {
        "schema": 1,
        "source": {
            "repository": "https://github.com/cmu-sei/secure-coding-standards",
            "commit": commit, "commit_date": cdate,
            "license": "CC BY 4.0 (text), MIT (code examples)",
        },
        "counts": {},
        "rules": rules,
    }
    for lang in STANDARDS:
        for kind in ("rule", "recommendation"):
            n = sum(1 for r in rules if r["lang"] == lang and r["kind"] == kind)
            if n:
                out["counts"][f"{lang}_{kind}"] = n
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                     encoding="utf-8")
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(
        "# Rule counts: parsed versus the standards' own index pages\n\n"
        f"Source commit: `{commit}` ({cdate})\n\n"
        "| Standard | Kind | Listed in index pages | Parsed | In index but not parsed "
        "| Parsed but not in index |\n|---|---|---|---|---|---|\n"
        + "\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))
    print("counts:", out["counts"], "commit:", commit)
    if mismatch and not a.allow_mismatch:
        print("MISMATCH between index pages and parsed files", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
