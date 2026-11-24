"""Build the card images used in the profile README.

Every card is one self-contained SVG (screenshots and icons inlined as data, no external
references) in a dark and a light variant, so GitHub can serve it through its image proxy
and the README can switch with <picture> and prefers-color-scheme.

    python scripts/capture_shots.py     # refresh the product screenshots (optional)
    python scripts/build_cards.py       # writes assets/card-*.svg, about-*, contact-*,
                                        # assets/skills-*.svg

Text is wrapped by measuring it with Segoe UI (Windows fonts), with a safety margin for
the wider system fonts other viewers get.
"""

from __future__ import annotations

import base64
from pathlib import Path
from xml.dom import minidom
from xml.sax.saxutils import escape

from PIL import ImageFont

from build_icon_grids import SIMPLE, fetch, place, prefix_ids, skill_tile

ROOT = Path(__file__).resolve().parent.parent
ASSETS, SHOTS = ROOT / "assets", ROOT / "assets" / "shots"
FONT_DIR = Path("C:/Windows/Fonts")
SANS = '-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif'
MONO = '"JetBrains Mono","Cascadia Code",Consolas,"SF Mono",Menlo,monospace'
SAFETY = 1.08  # other platforms' UI fonts run a little wider than Segoe UI

THEME = {
    "dark": dict(card="#161b22", border="#30363d", title="#f0f6fc", text="#c9d1d9",
                 muted="#8b949e", accent="#7ee2a8", rule="#21262d", chip="#21262d"),
    "light": dict(card="#ffffff", border="#d0d7de", title="#1f2328", text="#424a53",
                  muted="#656d76", accent="#1a7f37", rule="#d8dee4", chip="#f6f8fa"),
}

_fonts: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def text_width(text: str, size: int, weight: str = "regular") -> float:
    file = {"regular": "segoeui.ttf", "semibold": "seguisb.ttf", "bold": "segoeuib.ttf"}[weight]
    key = (file, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(str(FONT_DIR / file), size)
    return _fonts[key].getlength(text) * SAFETY


def wrap(text: str, size: int, width: float, max_lines: int) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if text_width(trial, size) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    lines.append(line)
    if len(lines) > max_lines:
        raise ValueError(f"text needs {len(lines)} lines, max {max_lines}: {text!r}")
    return lines


def svg_doc(width: int, height: int, body: str, label: str) -> str:
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
           f'width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" '
           f'aria-label="{escape(label, {chr(34): "&quot;"})}">\n{body}\n</svg>\n')
    minidom.parseString(svg)  # fail loudly on broken XML instead of a blank image on GitHub
    return svg


def text_block(lines: list[str], x: float, y: float, size: int, lh: float, fill: str,
               weight: int = 400) -> str:
    out = [f'<text x="{x}" y="{y}" font-family=\'{SANS}\' font-size="{size}" '
           f'font-weight="{weight}" fill="{fill}">']
    for i, line in enumerate(lines):
        out.append(f'<tspan x="{x}" dy="{0 if i == 0 else lh}">{escape(line)}</tspan>')
    out.append("</text>")
    return "".join(out)


def write(name: str, svg: str) -> None:
    (ASSETS / name).write_text(svg, encoding="utf8")
    print(f"wrote {name} ({len(svg.encode()) // 1024} KB)")


# ---------------------------------------------------------------- product cards

PRODUCTS = [
    dict(slug="househunter", name="House Hunter", site="househunter.immo",
         pitch="Real-estate search for Belgium: six listing sites in one search, saved-search "
               "email alerts, market history and Stripe subscriptions.",
         stack="FastAPI, Celery, MongoDB, Next.js 16, Stripe"),
    dict(slug="skipy", name="Skipy", site="skipy.online",
         pitch="Online store and skip-the-line ordering for cafés and small shops: customers "
               "order and pay from their phone. Live in Belgium and Brazil.",
         stack="FastAPI, MongoDB, Celery, Next.js, Expo, Stripe"),
    dict(slug="hiddenbeer", name="HiddenBeer", site="hiddenbeer.com",
         pitch="First-beer-free offers at Brussels bars: find one on the map, sign in with a "
               "one-time code, redeem with a signed QR code.",
         stack="FastAPI, MongoDB geospatial, Next.js 15, Leaflet, Docker"),
    dict(slug="lovemail", name="Love Mail", site="lovemail.online",
         pitch="Paid digital love letters: pick a tone, add a song and photos, pay with Stripe "
               "and deliver by email or QR code.",
         stack="React, Vite, Express, TypeScript, Stripe"),
    dict(slug="wtech", name="W-Tech IT Solutions", site="wtechitsolutions.com",
         pitch="Company website: a static, SEO-first Next.js site with structured data, case "
               "studies, a blog and a contact form.",
         stack="Next.js, TypeScript, MongoDB"),
    dict(slug="cabinetflow", name="CabinetFlow", site="cabinet-flow.com",
         pitch="Patient management for practitioners in private practice, built around "
               "professional secrecy. Live site and demo; the clinical platform is pre-launch.",
         stack="React 19, TypeScript, Vite, Spring Boot, MongoDB"),
]

CARD_W, SHOT_H = 400, 200


def shot_area(p: dict, uid: str) -> str:
    """The top 400x200 of a product card: a screenshot of the live site."""
    clip = (f'<clipPath id="{uid}c"><path d="M0 12a12 12 0 0 1 12-12h{CARD_W - 24}'
            f'a12 12 0 0 1 12 12v{SHOT_H - 12}h-{CARD_W}z"/></clipPath>')
    data = base64.b64encode((SHOTS / f"{p['slug']}.jpg").read_bytes()).decode()
    img = (f'<image width="{CARD_W}" height="{SHOT_H}" preserveAspectRatio="xMidYMin slice" '
           f'href="data:image/jpeg;base64,{data}"/>')
    return f'<defs>{clip}</defs><g clip-path="url(#{uid}c)">{img}</g>'


def product_card(p: dict, theme: str) -> str:
    t = THEME[theme]
    uid = f"{p['slug']}{theme[0]}"
    pitch = wrap(p["pitch"], 13, CARD_W - 40, 3)
    height = 334
    body = [
        f'<rect x=".5" y=".5" width="{CARD_W - 1}" height="{height - 1}" rx="12" '
        f'fill="{t["card"]}" stroke="{t["border"]}"/>',
        shot_area(p, uid),
        f'<rect y="{SHOT_H}" width="{CARD_W}" height="1" fill="{t["border"]}"/>',
        f'<text x="20" y="232" font-family=\'{SANS}\' font-size="17" font-weight="600" '
        f'fill="{t["title"]}">{escape(p["name"])}</text>',
        f'<text x="{CARD_W - 20}" y="232" text-anchor="end" font-family=\'{SANS}\' font-size="12" '
        f'fill="{t["accent"]}">{escape(p["site"])}</text>',
        text_block(pitch, 20, 256, 13, 19, t["text"]),
        f'<text x="20" y="316" font-family=\'{SANS}\' font-size="12" fill="{t["muted"]}">'
        f'{escape(p["stack"])}</text>',
    ]
    return svg_doc(CARD_W, height, "\n".join(body), f'{p["name"]}: {p["pitch"]}')


# ---------------------------------------------------------------- repo cards

LANG_COLOR = {  # GitHub linguist colours
    "Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "HTML": "#e34c26",
    "CSS": "#663399", "Three.js": "#049ef4", "PyTorch": "#ee4c2c", "FastAPI": "#009688",
    "Stripe": "#635bff", "React": "#61dafb", "Supabase": "#3fcf8e", "LanceDB": "#e0b03f",
}

REPOS = [
    dict(name="backrooms-game", demo="Playable in the browser",
         desc="Found-footage horror game in the browser: a procedural Backrooms level seen "
              "through a 90s camcorder.",
         tags=["TypeScript", "Three.js"]),
    dict(name="rag-docs-assistant", demo=None,
         desc="Question answering over the FastAPI docs with hybrid retrieval (vector + BM25) "
              "and an evaluation harness that measures it.",
         tags=["Python", "LanceDB", "FastAPI"]),
    dict(name="fastapi-stripe-webhooks", demo=None,
         desc="Stripe webhooks that survive production: signature checks, idempotency, "
              "out-of-order events and the StripeObject.get() pitfall.",
         tags=["Python", "FastAPI", "Stripe"]),
    dict(name="movie-helper", demo=None,
         desc="Group movie picker: friends join a room, vote on a TMDB deck, and head-to-head "
              "rounds narrow it to one winner.",
         tags=["TypeScript", "React", "Python"]),
    dict(name="primordial", demo=None,
         desc="Artificial-life simulation: neural-network particles evolve by selection alone, "
              "with a PyTorch engine and a browser viewer.",
         tags=["Python", "PyTorch", "TypeScript"]),
    dict(name="marketplace-directory-template", demo="Live demo",
         desc="Shop directory for food courts and market halls, configured from one file and "
              "a CSV. No build step.",
         tags=["JavaScript", "HTML", "CSS"]),
    dict(name="fastapi-vs-drf-comparison", demo=None,
         desc="The same CRUD API built in FastAPI + SQLModel and in Django REST Framework, "
              "compared side by side.",
         tags=["Python", "FastAPI"]),
    dict(name="planetjersey", demo=None,
         desc="Football-kit storefront with catalog filters, search and a cart drawer.",
         tags=["TypeScript", "React"]),
    dict(name="qr-code-creator", demo=None,
         desc="Command-line tool that generates QR codes with a centred logo and rounded "
              "corners, tested by decoding the output.",
         tags=["Python"]),
    dict(name="bis2-scraper", demo=None,
         desc="Scrape-to-dashboard pipeline: scrapers upsert into Supabase Postgres on a daily "
              "GitHub Actions schedule.",
         tags=["Python", "Supabase"]),
]

REPO_ICON = ("M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5"
             "a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495"
             " 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25"
             " 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0"
             " 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z")  # GitHub Octicons "repo" (MIT)


def repo_card(r: dict, theme: str) -> str:
    t = THEME[theme]
    height = 150
    desc = wrap(r["desc"], 13, CARD_W - 40, 3)
    body = [
        f'<rect x=".5" y=".5" width="{CARD_W - 1}" height="{height - 1}" rx="10" '
        f'fill="{t["card"]}" stroke="{t["border"]}"/>',
        f'<path transform="translate(20 21)" d="{REPO_ICON}" fill="{t["muted"]}"/>',
        f'<text x="44" y="34" font-family=\'{SANS}\' font-size="15" font-weight="600" '
        f'fill="{t["accent"]}">{escape(r["name"])}</text>',
        text_block(desc, 20, 62, 13, 19, t["text"]),
    ]
    x = 20
    for tag in r["tags"]:
        body.append(f'<circle cx="{x + 5}" cy="{height - 23}" r="5" fill="{LANG_COLOR[tag]}"/>')
        body.append(f'<text x="{x + 15}" y="{height - 19}" font-family=\'{SANS}\' font-size="12" '
                    f'fill="{t["muted"]}">{escape(tag)}</text>')
        x += 15 + text_width(tag, 12) + 16
    if r["demo"]:
        w = text_width(r["demo"], 12) + 24
        body.append(f'<rect x="{CARD_W - 20 - w}" y="{height - 37}" width="{w}" height="22" rx="11" '
                    f'fill="none" stroke="{t["accent"]}"/>')
        body.append(f'<text x="{CARD_W - 20 - w / 2}" y="{height - 22}" text-anchor="middle" '
                    f'font-family=\'{SANS}\' font-size="12" fill="{t["accent"]}">'
                    f'{escape(r["demo"])}</text>')
    return svg_doc(CARD_W, height, "\n".join(body), f'{r["name"]}: {r["desc"]}')


# ---------------------------------------------------------------- about: how I work

# How a piece of work goes from a problem to production, on any product. Each step is a habit with evidence:
# local-first runs, CI on every public repo, docs/ai-context decision records, Search Console and log reviews.
PROCESS = [
    ("Understand", "Start from the user's problem, not from the stack"),
    ("Model", "The data model and the API contract before screens"),
    ("Build", "Small changes on a branch, each with its tests"),
    ("Verify", "Run it end to end locally before any server sees it"),
    ("Ship", "Green CI, then deploy to servers I run myself"),
    ("Watch", "Logs, Search Console and real usage after a release"),
    ("Record", "Decisions and known issues written down in the repo"),
]


def about_process(theme: str) -> str:
    t = THEME[theme]
    width, row_h, top = 400, 46, 82
    height = top + len(PROCESS) * row_h - 8
    body = [
        f'<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="12" '
        f'fill="{t["card"]}" stroke="{t["border"]}"/>',
        f'<text x="24" y="34" font-family=\'{SANS}\' font-size="16" font-weight="600" '
        f'fill="{t["title"]}">How I work</text>',
        f'<text x="24" y="54" font-family=\'{SANS}\' font-size="12" fill="{t["muted"]}">'
        f'From a problem to something running in production</text>',
        # the rail that joins the steps: a real sequence, each step feeds the next
        f'<rect x="31" y="{top + 2}" width="2" height="{(len(PROCESS) - 1) * row_h}" '
        f'fill="{t["rule"]}"/>',
    ]
    for i, (step, detail) in enumerate(PROCESS):
        y = top + i * row_h
        body.append(f'<circle cx="32" cy="{y + 2}" r="6" fill="{t["card"]}" stroke="{t["accent"]}" '
                    f'stroke-width="2"/>')
        body.append(f'<text x="52" y="{y + 7}" font-family=\'{SANS}\' font-size="14" '
                    f'font-weight="600" fill="{t["title"]}">{escape(step)}</text>')
        body.append(f'<text x="52" y="{y + 25}" font-family=\'{SANS}\' font-size="12" '
                    f'fill="{t["muted"]}">{escape(detail)}</text>')
    label = "How I work: " + "; ".join(f"{s}: {d}" for s, d in PROCESS)
    return svg_doc(width, height, "\n".join(body), label)


# ---------------------------------------------------------------- contact buttons

ICONS = {
    "linkedin": ("https://cdn.jsdelivr.net/npm/devicon@2.16.0/icons/linkedin/linkedin-plain.svg", "#0A66C2"),
    "email": ("https://cdn.jsdelivr.net/npm/@primer/octicons@19.15.0/build/svg/mail-16.svg", None),
    "site": ("https://cdn.jsdelivr.net/npm/@primer/octicons@19.15.0/build/svg/globe-16.svg", None),
    "calendar": ("https://cdn.jsdelivr.net/npm/@primer/octicons@19.15.0/build/svg/calendar-16.svg", None),
    "coffee": ("https://cdn.jsdelivr.net/npm/simple-icons@13.21.0/icons/buymeacoffee.svg", None),
}
CONTACTS = [("linkedin", "LinkedIn"), ("email", "luisedu.ge@gmail.com"), ("calendar", "Book a 30-min call"),
            ("site", "W-Tech IT Solutions"), ("coffee", "Buy me a coffee"), ("status", "Open to EU and remote roles")]


def contact_button(key: str, label: str, theme: str) -> str:
    t = THEME[theme]
    height, pad, icon = 36, 14, 16
    width = round(pad + icon + 9 + text_width(label, 13, "semibold") + pad)
    body = [f'<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="18" '
            f'fill="{t["card"]}" stroke="{t["border"]}"/>']
    if key == "status":
        # The one moving thing on the page: a slow pulse on the availability dot.
        body.insert(0, '<style>.pulse{transform-box:fill-box;transform-origin:center;'
                       'animation:pulse 2.4s ease-out infinite}'
                       '@keyframes pulse{from{transform:scale(1);opacity:.55}'
                       'to{transform:scale(2.6);opacity:0}}'
                       '@media (prefers-reduced-motion:reduce){.pulse{animation:none;opacity:0}}</style>')
        body.append(f'<circle class="pulse" cx="{pad + 8}" cy="18" r="4.5" fill="#3cb371"/>')
        body.append(f'<circle cx="{pad + 8}" cy="18" r="4.5" fill="#3cb371"/>')
    else:
        url, colour = ICONS[key]
        body.append(place(fetch(url), pad, 10, icon, colour or t["text"]))
    body.append(f'<text x="{pad + icon + 9}" y="23" font-family=\'{SANS}\' font-size="13" '
                f'font-weight="600" fill="{t["title"]}">{escape(label)}</text>')
    return svg_doc(width, height, "\n".join(body), label)


# ---------------------------------------------------------------- where I write and speak

# Same card grammar as the repo cards (two per row at 49%): icon, name in the accent colour, handle, one line.
# Icons stay monochrome in the theme's title colour so no brand colour fights the green accent.
WRITING = [
    dict(slug="devto", name="Dev Community", handle="@luiseduardoge", icon=SIMPLE.format("devdotto"),
         desc="Hands-on articles, with the code that goes with them"),
    dict(slug="hashnode", name="Hashnode", handle="@luiseduardoge", icon=SIMPLE.format("hashnode"),
         desc="Long-form articles on production problems"),
    dict(slug="linkedin", name="LinkedIn articles", handle="luisgespindola", icon=ICONS["linkedin"][0],
         desc="Shorter takes for people hiring and building products"),
    dict(slug="speakerdeck", name="Speaker Deck", handle="luiseduardoge", icon=SIMPLE.format("speakerdeck"),
         desc="Slides from my talks"),
    dict(slug="sessionize", name="Sessionize", handle="luiseduardoge", icon=SIMPLE.format("sessionize"),
         desc="Speaker profile for conference and meetup organisers"),
    dict(slug="coffee", name="Buy Me a Coffee", handle="luiseduardoge", icon=SIMPLE.format("buymeacoffee"),
         desc="If an article or one of my repos saved you some time"),
]


def writing_card(w: dict, theme: str) -> str:
    t = THEME[theme]
    height = 86
    handle_x = 56 + text_width(w["name"], 15, "semibold") + 8
    body = [
        f'<rect x=".5" y=".5" width="{CARD_W - 1}" height="{height - 1}" rx="10" '
        f'fill="{t["card"]}" stroke="{t["border"]}"/>',
        place(fetch(w["icon"]), 20, 17, 24, t["title"]),
        f'<text x="56" y="35" font-family=\'{SANS}\' font-size="15" font-weight="600" '
        f'fill="{t["accent"]}">{escape(w["name"])}</text>',
        f'<text x="{handle_x:.0f}" y="35" font-family=\'{SANS}\' font-size="12" '
        f'fill="{t["muted"]}">{escape(w["handle"])}</text>',
        f'<text x="20" y="66" font-family=\'{SANS}\' font-size="13" '
        f'fill="{t["text"]}">{escape(w["desc"])}</text>',
    ]
    return svg_doc(CARD_W, height, "\n".join(body), f'{w["name"]} ({w["handle"]}): {w["desc"]}')


# ---------------------------------------------------------------- skills: levels with evidence

ADVANCED = [
    ("python", "Python", "House Hunter, Skipy, HiddenBeer and 7 public repos"),
    ("fastapi", "FastAPI", "the API of House Hunter, Skipy and HiddenBeer"),
    ("ts", "TypeScript", "Love Mail, backrooms-game, movie-helper"),
    ("react", "React", "House Hunter, Love Mail, movie-helper"),
    ("nextjs", "Next.js", "House Hunter, Skipy, HiddenBeer, W-Tech"),
    ("mongodb", "MongoDB", "House Hunter, Skipy, HiddenBeer, W-Tech"),
]
INTERMEDIATE = [
    ("stripe", "Stripe", "payments in House Hunter, Love Mail, Skipy"),
    ("docker", "Docker", "HiddenBeer images built on GHCR"),
    ("nodejs", "Node.js", "the Express API of Love Mail"),
    ("expo", "Expo", "the Skipy mobile app"),
    ("postgres", "PostgreSQL", "bis2-scraper on Supabase"),
]


def skill_icon(key: str) -> str:
    if key == "stripe":
        inner = place(fetch(SIMPLE.format("stripe")), 56, 56, 144, "#ffffff")
        return (f'<svg width="256" height="256" viewBox="0 0 256 256"><rect width="256" '
                f'height="256" rx="60" fill="#635BFF"/>{inner}</svg>')
    if key == "expo":
        inner = place(fetch(SIMPLE.format("expo")), 56, 56, 144, "#ffffff")
        return (f'<svg width="256" height="256" viewBox="0 0 256 256"><rect width="256" '
                f'height="256" rx="60" fill="#242938"/>{inner}</svg>')
    return skill_tile(key)


def skills_panel(rows: list[tuple[str, str, str]], title: str, note: str, icons: dict,
                 theme: str) -> str:
    t = THEME[theme]
    width, row_h, top = 400, 46, 70
    height = top + len(ADVANCED) * row_h + 6  # both panels share one height so they line up
    body = [
        f'<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="12" '
        f'fill="{t["card"]}" stroke="{t["border"]}"/>',
        f'<text x="20" y="32" font-family=\'{SANS}\' font-size="16" font-weight="600" '
        f'fill="{t["title"]}">{escape(title)}</text>',
        f'<text x="20" y="52" font-family=\'{SANS}\' font-size="12" fill="{t["muted"]}">'
        f'{escape(note)}</text>',
    ]
    for i, (key, name, evidence) in enumerate(rows):
        y = top + i * row_h
        body.append(f'<rect x="20" y="{y - 4}" width="{width - 40}" height="1" fill="{t["rule"]}"/>')
        body.append(place(prefix_ids(icons[key], f"{key}{theme[0]}_"), 20, y + 6, 30))
        body.append(f'<text x="62" y="{y + 18}" font-family=\'{SANS}\' font-size="14" '
                    f'font-weight="600" fill="{t["title"]}">{escape(name)}</text>')
        body.append(f'<text x="62" y="{y + 35}" font-family=\'{SANS}\' font-size="12" '
                    f'fill="{t["muted"]}">{escape(evidence)}</text>')
    label = f"{title}: " + "; ".join(f"{n} ({e})" for _, n, e in rows)
    return svg_doc(width, height, "\n".join(body), label)


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    for theme in THEME:
        for p in PRODUCTS:
            write(f"card-product-{p['slug']}-{theme}.svg", product_card(p, theme))
        for r in REPOS:
            write(f"card-repo-{r['name']}-{theme}.svg", repo_card(r, theme))
    for theme in THEME:
        write(f"about-process-{theme}.svg", about_process(theme))
        for key, label in CONTACTS:
            write(f"contact-{key}-{theme}.svg", contact_button(key, label, theme))
        for w in WRITING:
            write(f"card-writing-{w['slug']}-{theme}.svg", writing_card(w, theme))
    icons = {key: skill_icon(key) for key, _, _ in ADVANCED + INTERMEDIATE}
    for theme in THEME:
        write(f"skills-advanced-{theme}.svg",
              skills_panel(ADVANCED, "Advanced", "What my products in production run on",
                           icons, theme))
        write(f"skills-intermediate-{theme}.svg",
              skills_panel(INTERMEDIATE, "Intermediate", "Used in shipped work, one or two projects each",
                           icons, theme))


if __name__ == "__main__":
    main()
