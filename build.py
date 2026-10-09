#!/usr/bin/env python3
"""Génère le site statique dans public/.

Usage :
    pip install -r requirements.txt
    python build.py          # pages, SEO, icônes, QR code
    python build.py --og     # + images de partage (nécessite Playwright)

Les fichiers posés à la main dans public/ (cv/, assets/fonts/) ne sont pas touchés.
"""
import base64
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markupsafe import Markup

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
CONTENT = ROOT / "content"
OUT = ROOT / "public"
ASSETS = OUT / "assets"

GOLD = "#B3820F"
TEAL = "#0A6B64"
NAVY = "#13203A"
SAND = "#F5F0E4"

# Exécuté avant le premier rendu : applique le thème choisi sans flash.
# Son empreinte SHA-256 est autorisée dans la CSP (public/_headers).
THEME_SCRIPT = (
    "(function(){var d=document.documentElement;"
    "d.className=d.className.replace('no-js','js');"
    "try{var t=localStorage.getItem('hd-theme');"
    "if(t==='light'||t==='dark')d.setAttribute('data-theme',t);}catch(e){}})();"
)


def load(name):
    return json.loads((CONTENT / f"{name}.json").read_text(encoding="utf-8"))


def short_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:10]


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- géométrie
def star_points(cx=200, cy=200, r=148):
    """Huit nœuds autour du médaillon, un tous les 45°."""
    pts = []
    for k in range(8):
        a = math.radians(-90 + 45 * k)
        pts.append((round(cx + r * math.cos(a), 1), round(cy + r * math.sin(a), 1)))
    return pts


def octagram(cx, cy, half):
    """Contour de l'étoile à huit branches formée par deux carrés de demi-côté `half`."""
    outer = half * math.sqrt(2)
    inner = half / math.cos(math.radians(22.5))
    pts = []
    for k in range(16):
        ang = math.radians(-90 + 22.5 * k)
        rad = outer if k % 2 == 0 else inner
        pts.append(f"{cx + rad * math.cos(ang):.2f},{cy + rad * math.sin(ang):.2f}")
    return " ".join(pts)


def zellige_svg():
    """Tuile de 96 px : une étoile au centre, quatre quarts d'étoile aux coins,
    reliés par des diagonales. Répétée, elle donne un réseau continu."""
    s = 96
    c = s / 2
    half = 13
    tip = half * math.sqrt(2)
    stars = [(c, c), (0, 0), (s, 0), (0, s), (s, s)]
    polys = "".join(f'<polygon points="{octagram(x, y, half)}"/>' for x, y in stars)
    d = tip * math.cos(math.radians(45))
    lines = []
    for sx, sy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        x1, y1 = c + sx * d, c + sy * d
        x2, y2 = (0 if sx < 0 else s) - sx * d, (0 if sy < 0 else s) - sy * d
        lines.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"/>')
    # petits losanges sur les milieux des côtés
    diamonds = "".join(
        f'<rect x="{x - 4}" y="{y - 4}" width="8" height="8" transform="rotate(45 {x} {y})"/>'
        for x, y in [(c, 0), (c, s), (0, c), (s, c)]
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 {s} {s}">'
        f'<g fill="none" stroke="{GOLD}" stroke-width="1" stroke-opacity=".55">'
        f"{polys}{''.join(lines)}{diamonds}</g>"
        f'<g fill="{TEAL}" fill-opacity=".35"><circle cx="{c}" cy="{c}" r="2.2"/></g></svg>'
    )


def rule_svg():
    """Filet sous les titres : un trait, une petite étoile, un trait."""
    star = octagram(28, 6, 3.4)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="56" height="12" viewBox="0 0 56 12">'
        f'<g stroke="{GOLD}" stroke-width="1.4" fill="none" stroke-linecap="round">'
        '<line x1="1" y1="6" x2="20" y2="6"/><line x1="36" y1="6" x2="55" y2="6"/>'
        f'<polygon points="{star}"/></g></svg>'
    )


def favicon_svg():
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        f'<rect width="64" height="64" rx="14" fill="{NAVY}"/>'
        '<g fill="none" stroke-width="3.2" stroke-linejoin="round">'
        '<rect x="18" y="18" width="28" height="28" stroke="#3CC9BB"/>'
        '<rect x="18" y="18" width="28" height="28" stroke="#D4A017" transform="rotate(45 32 32)"/>'
        "</g></svg>"
    )


def raster_icons():
    """favicon.ico (16/32/48) et apple-touch-icon (180) dessinés avec Pillow."""
    from PIL import Image, ImageDraw

    def draw(size, rounded=True):
        scale = 8
        big = size * scale
        img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
        g = ImageDraw.Draw(img)
        radius = int(big * 14 / 64) if rounded else 0
        g.rounded_rectangle([0, 0, big - 1, big - 1], radius=radius, fill=NAVY)
        c = big / 2
        half = big * 14 / 64
        width = max(2, int(big * 3.2 / 64))
        for rot, color in [(0, "#3CC9BB"), (45, "#D4A017")]:
            pts = []
            for k in range(4):
                a = math.radians(45 + 90 * k + rot)
                pts.append((c + half * math.sqrt(2) * math.cos(a), c + half * math.sqrt(2) * math.sin(a)))
            g.line(pts + [pts[0]], fill=color, width=width, joint="curve")
        return img.resize((size, size), Image.LANCZOS)

    draw(48).save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    draw(180, rounded=False).convert("RGB").save(ASSETS / "apple-touch-icon.png", optimize=True)
    draw(192).save(ASSETS / "icon-192.png", optimize=True)
    draw(512).save(ASSETS / "icon-512.png", optimize=True)


def qr_svg(url):
    import qrcode
    import qrcode.image.svg

    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    m = qr.get_matrix()
    n = len(m)
    path = []
    for y, row in enumerate(m):
        for x, cell in enumerate(row):
            if cell:
                path.append(f"M{x} {y}h1v1h-1z")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" shape-rendering="crispEdges">'
        f'<rect width="{n}" height="{n}" fill="#fff"/><path fill="{NAVY}" d="{"".join(path)}"/></svg>'
    )


# ---------------------------------------------------------------- SEO
def jsonld(site, c, page_url):
    base = site["base_url"]
    person_id = f"{base}/#person"
    graph = [
        {
            "@type": "ProfilePage",
            "@id": f"{page_url}#page",
            "url": page_url,
            "name": c["meta"]["title"],
            "description": c["meta"]["description"],
            "inLanguage": c["lang"],
            "dateModified": site["date_modified"],
            "isPartOf": {"@id": f"{base}/#website"},
            "mainEntity": {"@id": person_id},
        },
        {
            "@type": "Person",
            "@id": person_id,
            "name": site["name"],
            "alternateName": site["alternate_names"],
            "givenName": "Haitham",
            "familyName": "Dhaimi",
            "url": f"{base}/",
            "image": f"{base}/assets/og-fr.png",
            "jobTitle": c["meta"]["job_title"],
            "email": f"mailto:{site['email']}",
            "address": {"@type": "PostalAddress", "addressLocality": "Casablanca", "addressCountry": "MA"},
            "affiliation": {
                "@type": "CollegeOrUniversity",
                "name": "SUPTECH-SANTÉ",
                "parentOrganization": {"@type": "CollegeOrUniversity", "name": "Université Internationale Bleue"},
                "address": {"@type": "PostalAddress", "addressLocality": "Mohammedia", "addressCountry": "MA"},
            },
            "alumniOf": {"@type": "HighSchool", "name": "Lycée Alexandre"},
            "knowsAbout": site["knows_about"],
            "knowsLanguage": ["ar", "fr", "en"],
            "sameAs": [site["linkedin"], site["github"]],
        },
        {
            "@type": "WebSite",
            "@id": f"{base}/#website",
            "url": f"{base}/",
            "name": site["name"],
            "inLanguage": [l["code"] for l in site["languages"]],
            "publisher": {"@id": person_id},
        },
    ]
    text = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    return Markup(text.replace("</", "<\\/"))


def sitemap(site):
    base = site["base_url"]
    alts = "".join(
        f'\n    <xhtml:link rel="alternate" hreflang="{l["code"]}" href="{base}{l["path"]}"/>' for l in site["languages"]
    ) + f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{base}/"/>'
    urls = "".join(
        f"\n  <url>\n    <loc>{base}{l['path']}</loc>\n    <lastmod>{site['date_modified']}</lastmod>{alts}\n  </url>"
        for l in site["languages"]
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">' + urls + "\n</urlset>\n"
    )


def headers(script_hash):
    csp = (
        "default-src 'self'; "
        f"script-src 'self' 'sha256-{script_hash}'; "
        "style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; "
        "object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'; "
        "upgrade-insecure-requests"
    )
    return f"""/*
  Content-Security-Policy: {csp}
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), interest-cohort=()
  Cross-Origin-Opener-Policy: same-origin
  Strict-Transport-Security: max-age=31536000

/assets/fonts/*
  Cache-Control: public, max-age=31536000, immutable

/assets/style.css
  Cache-Control: public, max-age=31536000, immutable

/assets/main.js
  Cache-Control: public, max-age=31536000, immutable

/cv/*
  Cache-Control: public, max-age=3600
  X-Robots-Tag: noindex

/404.html
  X-Robots-Tag: noindex
"""


# ---------------------------------------------------------------- pages
def build(make_og=False):
    site = load("site")
    pages = {l["code"]: load(l["code"]) for l in site["languages"]}

    ASSETS.mkdir(parents=True, exist_ok=True)
    for name in ("style.css", "main.js"):
        shutil.copyfile(SRC / "assets" / name, ASSETS / name)
    write(ASSETS / "zellige.svg", zellige_svg())
    write(ASSETS / "rule.svg", rule_svg())
    write(ASSETS / "favicon.svg", favicon_svg())
    write(ASSETS / "qr.svg", qr_svg(site["base_url"] + "/"))
    raster_icons()

    css_v = short_hash((ASSETS / "style.css").read_bytes())
    js_v = short_hash((ASSETS / "main.js").read_bytes())
    script_hash = base64.b64encode(hashlib.sha256(THEME_SCRIPT.encode()).digest()).decode()

    env = Environment(loader=FileSystemLoader(SRC / "templates"), autoescape=True,
                      undefined=StrictUndefined, trim_blocks=False, lstrip_blocks=False)
    tpl = env.get_template("page.html")
    locales = {code: c["locale"] for code, c in pages.items()}

    for code, c in pages.items():
        page_url = site["base_url"] + c["path"]
        main_cv_lang = "en" if code == "en" else "fr"
        other_cv_lang = "fr" if main_cv_lang == "en" else "en"
        html = tpl.render(
            c=c,
            site=site,
            theme_script=Markup(THEME_SCRIPT),
            page_url=page_url,
            other_locales=[v for k, v in locales.items() if k != code],
            preload_font="ibm-plex-sans-arabic-arabic-400-normal.woff2" if code == "ar"
            else "ibm-plex-sans-latin-400-normal.woff2",
            css_v=css_v,
            js_v=js_v,
            jsonld=jsonld(site, c, page_url),
            cv_main=site["cv"][main_cv_lang],
            cv_other=site["cv"][other_cv_lang],
            cv_other_lang=other_cv_lang,
            star_points=star_points(),
        )
        target = OUT / c["path"].strip("/") / "index.html" if c["path"] != "/" else OUT / "index.html"
        write(target, html)
        print("page", target.relative_to(ROOT))

    nf = env.get_template("404.html").render(site=site, pages=pages, theme_script=Markup(THEME_SCRIPT), css_v=css_v)
    write(OUT / "404.html", nf)

    write(OUT / "sitemap.xml", sitemap(site))
    write(OUT / "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {site['base_url']}/sitemap.xml\n")
    write(OUT / "_headers", headers(script_hash))
    write(OUT / "site.webmanifest", json.dumps({
        "name": site["name"], "short_name": "H. Dhaimi", "start_url": "/", "display": "browser",
        "background_color": SAND, "theme_color": SAND,
        "icons": [{"src": "/assets/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/assets/icon-512.png", "sizes": "512x512", "type": "image/png"}],
    }, ensure_ascii=False, indent=2))

    if make_og:
        from tools.og import make_og_images
        make_og_images(site, pages, OUT)

    print("CSP script hash: sha256-" + script_hash)


if __name__ == "__main__":
    build(make_og="--og" in sys.argv)
