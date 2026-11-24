"""Build the labelled icon grids used in the profile README.

Each grid is one self-contained SVG (icons inlined, no external references), in a dark
and a light variant, so GitHub can serve it through its image proxy.

    python scripts/build_icon_grids.py      # writes assets/grid-*.svg

Icon sources (pinned):
  skillicons.dev                       tech-stack tiles
  @lobehub/icons-static-svg@1.102.0    AI tool logos (MIT)
  simple-icons@16.36.0                 platform logos (CC0)
  devicon@2.16.0                       Playwright logo (MIT)
  remotion-dev/remotion                Remotion logo
"""

from __future__ import annotations

import re
import urllib.request
from pathlib import Path
from xml.dom import minidom
from xml.sax.saxutils import escape

ASSETS = Path(__file__).resolve().parent.parent / "assets"
LOBE = "https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@1.102.0/icons/{}.svg"
SIMPLE = "https://cdn.jsdelivr.net/npm/simple-icons@16.36.0/icons/{}.svg"
DEVICON = "https://cdn.jsdelivr.net/npm/devicon@2.16.0/icons/{}.svg"
SKILL = "https://skillicons.dev/icons?i={}&theme=dark"
REMOTION = "https://raw.githubusercontent.com/remotion-dev/remotion/main/packages/brand/public/logo/remotion/logo.svg"

TILE_BG = "#242938"  # same tile colour as skillicons' dark theme
COLS, CELL_W, TILE, LABEL_GAP, ROW_H = 10, 82, 56, 18, 96
LABEL = {"dark": "#c9d1d9", "light": "#24292f"}

TECH = [
    ("python", "Python"), ("fastapi", "FastAPI"), ("flask", "Flask"), ("nodejs", "Node.js"),
    ("express", "Express"), ("ts", "TypeScript"), ("js", "JavaScript"), ("react", "React"),
    ("nextjs", "Next.js"), ("vite", "Vite"), ("tailwind", "Tailwind"), ("threejs", "Three.js"),
    ("flutter", "Flutter"), ("html", "HTML5"), ("css", "CSS3"), ("mongodb", "MongoDB"),
    ("postgres", "PostgreSQL"), ("mysql", "MySQL"), ("sqlite", "SQLite"), ("redis", "Redis"),
    ("firebase", "Firebase"), ("pytorch", "PyTorch"), ("php", "PHP"), ("wordpress", "WordPress"),
    ("docker", "Docker"), ("linux", "Linux"), ("ubuntu", "Ubuntu"), ("nginx", "nginx"),
    ("githubactions", "Actions"), ("git", "Git"), ("github", "GitHub"), ("vscode", "VS Code"),
    ("vitest", "Vitest"), ("pnpm", "pnpm"), ("bash", "Bash"),
]

# (label, url, colour for monochrome logos or None to keep the logo's own colours)
AI = [
    ("Claude", LOBE.format("claude-color"), None),
    ("Claude Code", LOBE.format("claudecode-color"), None),
    ("ChatGPT", LOBE.format("openai"), "#ffffff"),
    ("Codex CLI", LOBE.format("codex-color"), None),
    ("Copilot", LOBE.format("githubcopilot"), "#ffffff"),
    ("Cursor", LOBE.format("cursor"), "#ffffff"),
    ("Windsurf", LOBE.format("windsurf"), "#ffffff"),
    ("Gemini", LOBE.format("gemini-color"), None),
    ("Ollama", LOBE.format("ollama"), "#ffffff"),
]

PLATFORMS = [
    ("Stripe", SIMPLE.format("stripe"), "#635BFF"),
    ("Supabase", SIMPLE.format("supabase"), "#3FCF8E"),
    ("Cloudflare", SIMPLE.format("cloudflare"), "#F38020"),
    ("Hostinger", SIMPLE.format("hostinger"), "#8C6CF2"),
    ("Brevo", SIMPLE.format("brevo"), "#0B996E"),
    ("Search Console", SIMPLE.format("googlesearchconsole"), "#458CF5"),
    ("Mermaid", SIMPLE.format("mermaid"), "#FF3670"),
    ("Playwright", DEVICON.format("playwright/playwright-original"), None),
    ("Remotion", REMOTION, None),
]


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "profile-icon-builder"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf8")


def prefix_ids(svg: str, prefix: str) -> str:
    """Make ids unique so gradients from different icons can't collide in one file."""
    ids = set(re.findall(r'\bid="([^"]+)"', svg))
    for i in sorted(ids, key=len, reverse=True):
        svg = re.sub(rf'\bid="{re.escape(i)}"', f'id="{prefix}{i}"', svg)
        svg = re.sub(rf"url\(#{re.escape(i)}\)", f"url(#{prefix}{i})", svg)
        svg = re.sub(rf'href="#{re.escape(i)}"', f'href="#{prefix}{i}"', svg)
    return svg


def place(svg: str, x: float, y: float, size: float, fill: str | None = None) -> str:
    """Re-root an <svg> at (x, y) with the given size, keeping its viewBox."""
    svg = re.sub(r"<\?xml[^>]*>|<!--.*?-->|<title>.*?</title>", "", svg, flags=re.S).strip()
    if fill:
        svg = svg.replace("currentColor", fill)
    m = re.match(r"<svg\b([^>]*)>", svg)
    attrs = m.group(1)
    vb = re.search(r'viewBox="([^"]+)"', attrs)
    if vb:
        viewbox = vb.group(1)
    else:
        w = re.search(r'width="([\d.]+)', attrs).group(1)
        h = re.search(r'height="([\d.]+)', attrs).group(1)
        viewbox = f"0 0 {w} {h}"
    keep = " ".join(re.findall(r'\b(?:fill-rule|clip-rule|fill)="[^"]*"', attrs))
    if fill:
        keep = re.sub(r'\bfill="[^"]*"', "", keep)
        keep += f' fill="{fill}"'
    head = (f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="{viewbox}" '
            f'preserveAspectRatio="xMidYMid meet" {keep}>')
    return head + svg[m.end():]


def skill_tile(icon: str) -> str:
    raw = fetch(SKILL.format(icon))
    inner = re.search(r"<g transform=\"translate\(0, 0\)\">(.*)</g>", raw, flags=re.S).group(1).strip()
    if "undefined" in inner:
        raise ValueError(f"unknown skillicons id: {icon}")
    return inner  # a 256x256 tile <svg>


def logo_tile(url: str, fill: str | None) -> str:
    logo = place(fetch(url), 56, 56, 144, fill)
    return (f'<svg width="256" height="256" viewBox="0 0 256 256">'
            f'<rect width="256" height="256" rx="60" fill="{TILE_BG}"/>{logo}</svg>')


def grid(tiles: list[tuple[str, str]], theme: str) -> str:
    rows = (len(tiles) + COLS - 1) // COLS
    width, height = COLS * CELL_W, rows * ROW_H
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
             f'width="{width}" height="{height}" '
             f'viewBox="0 0 {width} {height}">',
             '<style>text{font:500 12px -apple-system,"Segoe UI",Helvetica,Arial,sans-serif}</style>']
    for n, (label, tile) in enumerate(tiles):
        col, row = n % COLS, n // COLS
        x, y = col * CELL_W + (CELL_W - TILE) / 2, row * ROW_H
        parts.append(place(prefix_ids(tile, f"i{n}_"), x, y, TILE))
        parts.append(f'<text x="{col * CELL_W + CELL_W / 2}" y="{y + TILE + LABEL_GAP}" '
                     f'text-anchor="middle" fill="{LABEL[theme]}">{escape(label)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    sets = {
        "tech": [(label, skill_tile(icon)) for icon, label in TECH],
        "ai": [(label, logo_tile(url, fill)) for label, url, fill in AI],
        "platforms": [(label, logo_tile(url, fill)) for label, url, fill in PLATFORMS],
    }
    ASSETS.mkdir(exist_ok=True)
    for name, tiles in sets.items():
        for theme in LABEL:
            out = ASSETS / f"grid-{name}-{theme}.svg"
            svg = grid(tiles, theme)
            minidom.parseString(svg)  # fail loudly on broken XML instead of a blank image
            out.write_text(svg, encoding="utf8")
            print(f"wrote {out.name} ({len(tiles)} icons)")


if __name__ == "__main__":
    main()
