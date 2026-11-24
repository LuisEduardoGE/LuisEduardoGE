"""Build the card images used in the profile README.

Every card is one self-contained SVG (screenshots and icons inlined as data, no external
references) in a dark and a light variant, so GitHub can serve it through its image proxy
and the README can switch with <picture> and prefers-color-scheme.

    python scripts/capture_shots.py     # refresh the product screenshots (optional)
    python scripts/build_cards.py       # writes assets/card-*.svg, assets/about-code.svg,
                                        # assets/skills-*.svg

Text is wrapped by measuring it with Segoe UI (Windows fonts), with a safety margin for
the wider system fonts other viewers get.
"""

from __future__ import annotations

import base64
import re
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
    dict(slug="caab", name="CAAB legal platform", site="Brazil",
         pitch="Custom WordPress engine for the Brazilian legal market: lawyer profiles with "
               "custom search, a classifieds engine and plugins.",
         stack="PHP, WordPress, MySQL, JavaScript"),
]

CARD_W, SHOT_H = 400, 200


def shot_area(p: dict, uid: str) -> str:
    """The top 400x200 of a product card: a real screenshot, or a panel when there is none."""
    clip = (f'<clipPath id="{uid}c"><path d="M0 12a12 12 0 0 1 12-12h{CARD_W - 24}'
            f'a12 12 0 0 1 12 12v{SHOT_H - 12}h-{CARD_W}z"/></clipPath>')
    shot = SHOTS / f"{p['slug']}.jpg"
    if shot.exists():
        data = base64.b64encode(shot.read_bytes()).decode()
        img = (f'<image width="{CARD_W}" height="{SHOT_H}" preserveAspectRatio="xMidYMin slice" '
               f'href="data:image/jpeg;base64,{data}"/>')
        return f'<defs>{clip}</defs><g clip-path="url(#{uid}c)">{img}</g>'
    # No public site to show (CAAB): the one number that says what the platform carries.
    return (f'<defs>{clip}<linearGradient id="{uid}g" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="#1c3557"/><stop offset="1" stop-color="#0e1a2b"/>'
            f'</linearGradient></defs><g clip-path="url(#{uid}c)">'
            f'<rect width="{CARD_W}" height="{SHOT_H}" fill="url(#{uid}g)"/>'
            f'<text x="32" y="112" font-family=\'{SANS}\' font-size="54" font-weight="700" '
            f'fill="#f0f6fc">5,000+</text>'
            f'<text x="34" y="146" font-family=\'{SANS}\' font-size="17" fill="#b6c6dc">'
            f'professional profiles served</text></g>')


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


# ---------------------------------------------------------------- about: code window

CODE = [
    'class Luis(Developer):',
    '    role = "full-stack, lead developer"',
    '    experience = "4+ years"',
    '    based_in = "Belgium"',
    '    speaks = ["en", "pt", "fr", "es", "nl"]',
    '',
    '    api = ["Python", "FastAPI", "Celery"]',
    '    web = ["TypeScript", "React", "Next.js"]',
    '    data = ["MongoDB", "Postgres", "Redis"]',
    '',
    '    products_in_production = 6',
    '    contributions_last_year = 5_900',
]
TOKEN = re.compile(r'(?P<str>"[^"]*")|(?P<num>\b\d[\d_]*\b)|(?P<kw>\bclass\b)|'
                   r'(?P<cls>\bLuis\b)|(?P<base>\bDeveloper\b)|(?P<name>\b[a-z_]+\b(?= =))|'
                   r'(?P<other>.)')
CODE_COLOR = dict(str="#a5d6ff", num="#79c0ff", kw="#ff7b72", cls="#d2a8ff", base="#7ee2a8",
                  name="#ffa657", other="#c9d1d9")


def about_code() -> str:
    width, line_h, top = 400, 21, 66
    height = top + len(CODE) * line_h + 10
    body = [
        f'<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="12" fill="#0d1117" '
        f'stroke="#30363d"/>',
        '<circle cx="22" cy="20" r="5.5" fill="#ff5f57"/><circle cx="40" cy="20" r="5.5" '
        'fill="#febc2e"/><circle cx="58" cy="20" r="5.5" fill="#28c840"/>',
        f'<text x="{width / 2}" y="24" text-anchor="middle" font-family=\'{SANS}\' font-size="12" '
        f'fill="#8b949e">luis.py</text>',
        f'<rect y="39" width="{width}" height="1" fill="#21262d"/>',
    ]
    for i, line in enumerate(CODE):
        spans = []
        for m in TOKEN.finditer(line):
            kind = m.lastgroup
            spans.append(f'<tspan fill="{CODE_COLOR[kind]}">{escape(m.group())}</tspan>')
        body.append(f'<text x="22" y="{top + i * line_h}" xml:space="preserve" '
                    f'font-family=\'{MONO}\' font-size="13">{"".join(spans)}</text>')
    return svg_doc(width, height, "\n".join(body),
                   "luis.py: full-stack and lead developer, 4+ years, based in Belgium; Python, "
                   "FastAPI, TypeScript, React, Next.js, MongoDB, Postgres; 6 products in "
                   "production; 5,900+ contributions last year")


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
    write("about-code.svg", about_code())
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
