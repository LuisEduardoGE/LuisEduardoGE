"""Rewrite the "Latest articles" block of README.md from my published articles.

    python scripts/latest_articles.py            # fetch feeds, rewrite README.md if the list changed
    python scripts/latest_articles.py --check    # print the block, change nothing

Sources (public, published posts only, so drafts never show): the Dev.to API, the Hashnode blog's RSS and the
Medium RSS feed, plus scripts/manual-articles.json for platforms without a feed (DZone, LinkedIn, Substack before it
has a feed). The same article on several platforms becomes one line: the title links to the first platform in
PREFERRED order and the others follow as "also on". A feed that fails is skipped, never fatal: the block is only
rewritten from what was fetched, and an empty result keeps the README as it is.

Standard library only, so the GitHub Action needs no install step.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
MANUAL = Path(__file__).resolve().parent / "manual-articles.json"
START, END = "<!-- latest-articles:start -->", "<!-- latest-articles:end -->"
LIMIT = 5
UA = {"User-Agent": "Mozilla/5.0 (compatible; LuisEduardoGE-profile-articles)"}
PREFERRED = ["Dev.to", "Hashnode", "Medium", "Substack", "DZone", "LinkedIn"]
SOURCES = [
    ("Dev.to", "devto", "https://dev.to/api/articles?username=luiseduardoge&per_page=100"),
    ("Hashnode", "rss", "https://luiseduardoge.hashnode.dev/rss.xml"),
    ("Medium", "rss", "https://medium.com/feed/@luisedu.ge"),
]


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as res:  # noqa: S310 - fixed https URLs above
        return res.read().decode("utf-8", "replace")


def parse_devto(text: str) -> list[dict]:
    return [{"title": a["title"], "url": a["url"], "date": a["published_at"][:10]} for a in json.loads(text)
            if a.get("published_at")]


def parse_rss(text: str) -> list[dict]:
    out = []
    for item in re.findall(r"<item>(.*?)</item>", text, flags=re.DOTALL):
        def tag(name: str, block: str = item) -> str:
            m = re.search(rf"<{name}[^>]*>(.*?)</{name}>", block, flags=re.DOTALL)
            raw = m.group(1).strip() if m else ""
            return html.unescape(re.sub(r"^<!\[CDATA\[(.*)\]\]>$", r"\1", raw, flags=re.DOTALL)).strip()
        title, link, date = tag("title"), tag("link"), tag("pubDate")
        if not (title and link):
            continue
        try:
            day = parsedate_to_datetime(date).astimezone(timezone.utc).date().isoformat()
        except (TypeError, ValueError):
            day = ""
        out.append({"title": title, "url": re.sub(r"\?source=rss[^#]*$", "", link), "date": day})
    return out


def key(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def merge(per_platform: dict[str, list[dict]]) -> list[dict]:
    """One entry per article: earliest date, every platform's link, sorted newest first."""
    merged: dict[str, dict] = {}
    for platform, items in per_platform.items():
        for it in items:
            entry = merged.setdefault(key(it["title"]), {"title": it["title"], "date": it["date"], "links": {}})
            entry["links"].setdefault(platform, it["url"])
            if it["date"] and (not entry["date"] or it["date"] < entry["date"]):
                entry["date"] = it["date"]
    return sorted(merged.values(), key=lambda e: e["date"], reverse=True)


def render(articles: list[dict]) -> str:
    lines = []
    for a in articles[:LIMIT]:
        order = sorted(a["links"], key=lambda p: PREFERRED.index(p) if p in PREFERRED else len(PREFERRED))
        first, rest = order[0], order[1:]
        when = datetime.fromisoformat(a["date"]).strftime("%b %Y") if a["date"] else ""
        title = a["title"].replace("[", "(").replace("]", ")")
        also = (", also on " + ", ".join(f"[{p}]({a['links'][p]})" for p in rest)) if rest else ""
        lines.append(f"- **[{title}]({a['links'][first]})** ({when}) on {first}{also}")
    return "\n".join(lines)


def collect() -> dict[str, list[dict]]:
    found: dict[str, list[dict]] = {}
    for platform, kind, url in SOURCES:
        try:
            text = fetch(url)
            found[platform] = parse_devto(text) if kind == "devto" else parse_rss(text)
        except Exception as exc:  # noqa: BLE001 - one dead feed must not empty the list
            print(f"skip {platform}: {exc}", file=sys.stderr)
    if MANUAL.exists():
        for it in json.loads(MANUAL.read_text(encoding="utf-8")):
            found.setdefault(it["platform"], []).append(it)
    return found


def replace_block(readme: str, body: str) -> str:
    if START not in readme or END not in readme:
        raise SystemExit(f"README.md has no {START} ... {END} block")
    head, rest = readme.split(START, 1)
    _, tail = rest.split(END, 1)
    return f"{head}{START}\n{body}\n{END}{tail}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="print the block, don't write")
    args = ap.parse_args(argv)

    articles = merge(collect())
    body = render(articles) if articles else "_First articles coming soon._"
    print(body)
    if args.check:
        return 0
    readme = README.read_text(encoding="utf-8")
    current = readme.split(START, 1)[1].split(END, 1)[0].strip() if START in readme else ""
    if not articles and current and not current.startswith("_"):
        print("No articles fetched: keeping the current list.", file=sys.stderr)
        return 0
    updated = replace_block(readme, body)
    if updated != readme:
        README.write_text(updated, encoding="utf-8", newline="\n")
        print("README.md updated", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
