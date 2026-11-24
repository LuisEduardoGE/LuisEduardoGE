"""Capture the product screenshots used on the profile cards.

    python scripts/capture_shots.py           # writes assets/shots/<name>.jpg (1280x640 viewport crop)

Needs `pip install playwright pillow` and `playwright install chromium`.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "assets" / "shots"
SITES = {
    "househunter": "https://househunter.immo",
    "lovemail": "https://lovemail.online",
    "wtech": "https://wtechitsolutions.com",
    "skipy": "https://skipy.online/en",
    "hiddenbeer": "https://hiddenbeer.com/",
    "cabinetflow": "https://cabinet-flow.com/",
}
# Hide cookie / consent overlays so the screenshot shows the product, not a banner.
HIDE_OVERLAYS = """
for (const el of document.querySelectorAll('body *')) {
  const s = getComputedStyle(el);
  if ((s.position === 'fixed' || s.position === 'sticky') && el.offsetHeight < innerHeight * 0.6
      && /cookie|consent|gdpr|banner/i.test(el.className + ' ' + el.id + ' ' + el.innerText.slice(0, 200))) {
    el.style.display = 'none';
  }
}
"""
# HiddenBeer opens behind a full-screen age gate: hide it (nothing is accepted) and undo the blur.
HIDE_GATE = """
for (const el of document.querySelectorAll('body *')) {
  const s = getComputedStyle(el);
  if (s.position === 'fixed' && el.offsetWidth >= innerWidth * 0.9 && el.offsetHeight >= innerHeight * 0.9) {
    el.style.display = 'none';
  }
}
for (const el of document.querySelectorAll('*')) {
  el.style.filter = 'none';
  el.style.backdropFilter = 'none';
}
document.body.style.overflow = 'auto';
"""


def main(names: list[str]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1280, "height": 640}, device_scale_factor=1,
                                  locale="en-GB", color_scheme="light",
                                  ignore_https_errors=True,  # this machine intercepts TLS
                                  geolocation={"latitude": 50.8467, "longitude": 4.3525},  # Brussels
                                  permissions=["geolocation"])
        for name, url in SITES.items():
            if names and name not in names:
                continue
            page = ctx.new_page()
            page.goto(url, wait_until="load", timeout=60_000)
            page.wait_for_timeout(2500)
            page.evaluate(HIDE_OVERLAYS)
            if name == "hiddenbeer":
                page.evaluate(HIDE_GATE)
                page.wait_for_timeout(1500)
            png = page.screenshot()
            img = Image.open(io.BytesIO(png)).convert("RGB").resize((800, 400), Image.LANCZOS)
            img.save(OUT / f"{name}.jpg", quality=72, optimize=True, progressive=True)
            print(name, (OUT / f"{name}.jpg").stat().st_size // 1024, "KB")
            page.close()
        browser.close()


if __name__ == "__main__":
    main(sys.argv[1:])
