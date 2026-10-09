"""Images de partage 1200×630 (LinkedIn, WhatsApp, X…), une par langue.

Rendu avec Chromium via Playwright pour que l'arabe soit correctement lié
et que les polices soient exactement celles du site.
"""
import base64
import html
from pathlib import Path

TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}" dir="{dir}"><head><meta charset="utf-8"><style>
@font-face{{font-family:"Amiri";font-weight:700;src:url("{fonts}/amiri-latin-700-normal.woff2")}}
@font-face{{font-family:"Plex";font-weight:400;src:url("{fonts}/ibm-plex-sans-latin-400-normal.woff2");unicode-range:U+0000-024F,U+2000-206F}}
@font-face{{font-family:"Plex";font-weight:600;src:url("{fonts}/ibm-plex-sans-latin-600-normal.woff2");unicode-range:U+0000-024F,U+2000-206F}}
@font-face{{font-family:"Plex";font-weight:400;src:url("{fonts}/ibm-plex-sans-arabic-arabic-400-normal.woff2");unicode-range:U+0600-06FF,U+0750-077F,U+FB50-FDFF,U+FE70-FEFF}}
@font-face{{font-family:"Plex";font-weight:600;src:url("{fonts}/ibm-plex-sans-arabic-arabic-600-normal.woff2");unicode-range:U+0600-06FF,U+0750-077F,U+FB50-FDFF,U+FE70-FEFF}}
*{{box-sizing:border-box;margin:0}}
html,body{{width:1200px;height:630px}}
body{{background:#F5F0E4;color:#13203A;font-family:"Plex",sans-serif;position:relative;overflow:hidden}}
.pattern{{position:absolute;inset:0;background:url("{zellige}") 0 0/120px 120px;opacity:.75;
  -webkit-mask-image:radial-gradient(ellipse 60% 95% at {mask} 50%,#000 0%,transparent 72%)}}
.frame{{position:absolute;inset:28px;border:1.5px solid rgba(179,130,15,.45);border-radius:22px}}
.content{{position:absolute;inset-block:0;inset-inline-start:88px;width:690px;display:flex;flex-direction:column;justify-content:center;gap:22px}}
.kicker{{color:#0A6B64;font-weight:600;font-size:{kicker_size}px}}
h1{{font-family:"Amiri",serif;font-size:104px;line-height:1;font-weight:700}}
h1 span{{color:#7F5905}}
.title{{font-size:{title_size}px;line-height:1.35;font-weight:600;max-width:640px}}
.url{{align-self:flex-start;margin-block-start:14px;font-size:22px;color:#4A5470;direction:ltr;unicode-bidi:isolate;letter-spacing:.01em}}
.star{{position:absolute;inset-inline-end:110px;top:50%;width:300px;height:300px;transform:translateY(-50%)}}
</style></head><body>
<div class="pattern"></div><div class="frame"></div>
<div class="content">
  <p class="kicker">{kicker}</p>
  <h1 lang="en">Haitham <span>Dhaimi</span></h1>
  <p class="title">{title}</p>
  <p class="url">{url}</p>
</div>
<svg class="star" viewBox="0 0 400 400">
  <circle cx="200" cy="200" r="182" fill="none" stroke="rgba(179,130,15,.35)"/>
  <rect x="95" y="95" width="210" height="210" fill="none" stroke="#0A6B64" stroke-width="3"/>
  <rect x="95" y="95" width="210" height="210" fill="none" stroke="#B3820F" stroke-width="3" transform="rotate(45 200 200)"/>
  <circle cx="200" cy="200" r="78" fill="#FFFCF5" stroke="rgba(179,130,15,.35)"/>
  <path d="M126 200h34l11-28 15 60 15-92 15 108 12-48h46" fill="none" stroke="#0A6B64" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
</body></html>"""


def make_og_images(site, pages, out: Path):
    from playwright.sync_api import sync_playwright

    fonts = (out / "assets" / "fonts").resolve().as_uri()
    zellige = "data:image/svg+xml;base64," + base64.b64encode((out / "assets" / "zellige.svg").read_bytes()).decode()
    url = site["base_url"].replace("https://", "")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 630})
        for code, c in pages.items():
            rtl = c["dir"] == "rtl"
            doc = TEMPLATE.format(
                lang=code, dir=c["dir"], fonts=fonts, zellige=zellige,
                mask="15%" if rtl else "85%",
                kicker=html.escape(c["hero"]["kicker"]),
                title=html.escape(c["meta"]["og_description"]),
                url=html.escape(url),
                kicker_size=30 if rtl else 26,
                title_size=30 if rtl else 28,
            )
            tmp = out / f"_og_{code}.html"
            tmp.write_text(doc, encoding="utf-8")
            page.goto(tmp.resolve().as_uri())
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(300)
            page.screenshot(path=str(out / "assets" / f"og-{code}.png"))
            tmp.unlink()
            print("og", code)
        browser.close()
