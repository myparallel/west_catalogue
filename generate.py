#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Product Detail Page Generator (west_catalogue edition)
=======================================================
Generates product pages into products/<SKU>/ referencing 
shared assets/ for CSS/JS.

Usage:
    python generate.py <config.json>
    # output goes to products/<SKU>/
"""

import json
import os
import sys
import shutil


ROOT = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_DIR = os.path.join(ROOT, "products")


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def esc_js(text):
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'").replace("\n", "\\n").replace("\r", "")


def build_json_ld(cfg):
    p = cfg["product"]
    images = cfg.get("images", [])
    img_list = json.dumps([img.get("src", "") for img in images])
    return f"""{{
        "@context": "https://schema.org",
        "@type": "Product",
        "name": {json.dumps(p.get("name",""))},
        "sku": {json.dumps(p.get("sku",""))},
        "description": {json.dumps(p.get("description",""))},
        "brand": {{ "@type": "Brand", "name": {json.dumps(p.get("brand",""))} }},
        "image": {img_list},
        "manufacturer": {{
            "@type": "Organization",
            "name": {json.dumps(p.get("manufacturer",""))}
        }}
    }}"""


def build_nav(cfg):
    has_video = bool(cfg.get("video", {}).get("available", False))
    links = [
        ("../../index.html", "Catalog"),
        ("#overview", "Overview"),
        ("#highlights", "Highlights"),
        ("#gallery", "Gallery"),
    ]
    if has_video:
        links.append(("#video", "Video"))
    links += [
        ("#specifications", "Specifications"),
        ("#applications", "Applications"),
        ("#package", "Package"),
        ("#downloads", "Downloads"),
        ("#contact", "Contact"),
    ]
    return "".join(f'<a href="{href}">{label}</a>' for href, label in links)


def build_hero(cfg):
    p = cfg["product"]
    hero_img = cfg.get("hero_image") or cfg["images"][0]["src"]
    manual_pdf = cfg.get("manual_pdf", "")
    dl = os.path.basename(manual_pdf) if manual_pdf else ""
    page_num = p.get("page_number", 1)
    return f"""<section class="hero wrap" id="overview">
  <div class="hero-grid">
    <div>
      <div class="page-badge">Page {page_num}</div>
      <h1>{esc(p.get("name",""))}</h1>
      <p class="lead">{esc(p.get("lead",""))}</p>
      <div class="hero-actions">
        <button type="button" class="btn btn-primary btn-pdf" data-sku="{esc(p.get("sku",""))}">Download as PDF</button>
        <a class="btn btn-primary dl-link" href="{esc(manual_pdf)}" download="{esc(dl)}">Download Manual (PDF)</a>
        <button type="button" class="btn btn-secondary" id="quote-open-btn" data-open-quote>Request Quote</button>
      </div>
      <p class="doc-note">English PDF manual. For technical support or customized OEM versions, email us from <a href="#contact">Contact Information</a>.</p>
    </div>
    <div class="hero-visual">
      <img src="{esc(hero_img)}" alt="{esc(p.get("name",""))}" width="800" height="800" fetchpriority="high" />
    </div>
  </div>
</section>"""


def build_highlights(cfg):
    items = cfg.get("highlights", [])
    if not items:
        return ""
    cards = "".join(
        f'<div class="card"><h3>{esc(item["title"])}</h3><p>{esc(item["text"])}</p></div>\n'
        for item in items
    )
    return f"""<section class="wrap" id="highlights">
  <h2 class="section-title">Key Highlights</h2>
  <p class="section-sub">Precision monitoring meets rugged industrial design.</p>
  <div class="highlights">
    {cards}
  </div>
</section>"""


def build_gallery(cfg):
    images = cfg.get("images", [])
    if not images:
        return ""
    thumbs = ""
    first_active = True
    for img in images:
        src = esc(img.get("src", ""))
        alt = esc(img.get("alt", ""))
        active_class = ' is-active' if first_active else ''
        first_active = False
        thumbs += f"""<button type="button" class="{active_class.strip()}" data-full="{src}" data-alt="{alt}"><img src="{src}" alt="" width="120" height="90" loading="lazy" /></button>\n"""
    return f"""<section class="wrap" id="gallery">
  <h2 class="section-title">Product Gallery</h2>
  <p class="section-sub">Detailed views (Scroll thumbnails to browse).</p>
  <div class="gallery-layout gallery-layout--v2">
    <div class="stage" id="gallery-stage" aria-live="polite"></div>
    <div class="thumbs" role="tablist" aria-label="Gallery thumbnails">
      {thumbs}
    </div>
  </div>
</section>"""


def build_video(cfg):
    video = cfg.get("video", {})
    if not video.get("available"):
        return ""
    poster = esc(video.get("poster", ""))
    src = esc(video.get("src", ""))
    return f"""<section class="wrap" id="video">
  <h2 class="section-title">Product Video</h2>
  <p class="section-sub">Quick look at the {esc(cfg["product"].get("name",""))} in action.</p>
  <div class="video-container">
    <video controls preload="metadata" poster="{poster}">
      <source src="{src}" type="video/mp4" />
      Your browser does not support the video tag.
    </video>
  </div>
</section>"""


def build_specifications(cfg):
    specs = cfg.get("specifications", [])
    if not specs:
        return ""
    rows = "".join(
        f'<tr><th scope="row">{esc(s["label"])}</th><td>{esc(s["value"])}</td></tr>\n'
        for s in specs
    )
    return f"""<section class="wrap" id="specifications">
  <h2 class="section-title">Specifications</h2>
  <p class="section-sub">Technical parameters based on the product manual.</p>
  <div class="spec-table-wrap">
    <table class="spec">
      <tbody>
        {rows}
      </tbody>
    </table>
  </div>
</section>"""


def build_applications(cfg):
    apps = cfg.get("applications", [])
    if not apps:
        return ""
    cards = "".join(
        f'<div class="card"><h3>{esc(a["title"])}</h3><p>{esc(a["text"])}</p></div>\n'
        for a in apps
    )
    return f"""<section class="wrap" id="applications">
  <h2 class="section-title">Typical Applications</h2>
  <p class="section-sub">Optimized for diverse agricultural and environmental monitoring needs.</p>
  <div class="two-col">
    {cards}
  </div>
</section>"""


def build_package(cfg):
    items = cfg.get("package_items", [])
    if not items:
        return ""
    rows = ""
    for i, item in enumerate(items, 1):
        rows += f"<tr><td>{i}</td><td>{esc(item['item'])}</td><td>{esc(str(item['qty']))}</td></tr>\n"
    return f"""<section class="wrap" id="package">
  <h2 class="section-title">Standard Package</h2>
  <p class="section-sub">Standard configuration for the {esc(cfg["product"].get("sku",""))}.</p>
  <div class="spec-table-wrap">
    <table class="spec">
      <thead>
        <tr><th scope="col">#</th><th scope="col">Item</th><th scope="col">Qty</th></tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
  </div>
</section>"""


def build_downloads(cfg):
    manual_pdf = cfg.get("manual_pdf", "")
    if not manual_pdf:
        return ""
    dl = os.path.basename(manual_pdf)
    return f"""<section class="wrap" id="downloads">
  <h2 class="section-title">Downloads</h2>
  <p class="section-sub">Access technical documentation for the {esc(cfg["product"].get("name",""))}.</p>
  <div class="hero-actions">
    <a class="btn btn-primary dl-link" href="{esc(manual_pdf)}" download="{esc(dl)}">Download User Manual (PDF)</a>
  </div>
</section>"""


def build_contact(cfg):
    c = cfg.get("contact", {})
    return f"""<section class="wrap" id="contact">
  <h2 class="section-title">Contact Information</h2>
  <p class="section-sub">For quotations, lead times, and technical support.</p>
  <address class="contact-info">
    {c.get("address","")}<br />
    <a href="tel:{esc(c.get("phone",""))}">{esc(c.get("phone",""))}</a><br />
    <a href="mailto:{esc(c.get("email",""))}">{esc(c.get("email",""))}</a><br />
    {esc(c.get("hours",""))}
  </address>
</section>"""


def build_footer(cfg):
    p = cfg["product"]
    page_num = p.get("page_number", 1)
    return f"""<footer class="site-footer">
  <div class="wrap footer-meta">
    <span>{esc(p.get("manufacturer",""))} &middot; SKU {esc(p.get("sku",""))}</span>
    <span>Page {page_num} &middot; Product Catalogue</span>
  </div>
</footer>"""


def build_quote_modal(cfg):
    p = cfg["product"]
    return f"""<div class="quote-modal" id="quote-modal" role="dialog" aria-modal="true" aria-labelledby="quote-modal-title" aria-hidden="true">
  <div class="quote-modal__backdrop" data-close-quote tabindex="-1"></div>
  <div class="quote-modal__dialog">
    <h2 class="quote-modal__title" id="quote-modal-title">Request a quote</h2>
    <p class="quote-modal__lead">{esc(p.get("name",""))} - Tell us about your project.</p>
    <form class="quote-form" id="quote-form" novalidate>
      <div class="quote-form__row">
        <label for="quote-name">Full name <span aria-hidden="true">*</span></label>
        <input id="quote-name" name="name" type="text" autocomplete="name" required maxlength="120" />
      </div>
      <div class="quote-form__row">
        <label for="quote-company">Company <span aria-hidden="true">*</span></label>
        <input id="quote-company" name="company" type="text" autocomplete="organization" required maxlength="160" />
      </div>
      <div class="quote-form__row quote-form__row--half">
        <div>
          <label for="quote-email">Work email <span aria-hidden="true">*</span></label>
          <input id="quote-email" name="email" type="email" autocomplete="email" required maxlength="120" />
        </div>
        <div>
          <label for="quote-phone">Phone</label>
          <input id="quote-phone" name="phone" type="tel" autocomplete="tel" maxlength="40" />
        </div>
      </div>
      <div class="quote-form__row">
        <label for="quote-region">Country / region <span aria-hidden="true">*</span></label>
        <input id="quote-region" name="region" type="text" autocomplete="country-name" required maxlength="80" />
      </div>
      <div class="quote-form__row">
        <label for="quote-message">Application notes <span aria-hidden="true">*</span></label>
        <textarea id="quote-message" name="message" rows="4" required maxlength="2000" placeholder="Sensor types, network requirements, project scope..."></textarea>
      </div>
      <p class="quote-form__hint" id="quote-form-hint" role="status" aria-live="polite"></p>
      <div class="quote-form__actions">
        <button type="button" class="btn btn-secondary" data-close-quote>Cancel</button>
        <button type="submit" class="btn btn-primary">Send</button>
      </div>
    </form>
    <button type="button" class="quote-modal__close" data-close-quote aria-label="Close dialog">&times;</button>
  </div>
</div>"""


def generate_html(cfg):
    p = cfg["product"]
    title = f'{esc(p.get("name",""))} | {esc(p.get("sku",""))}'
    meta_desc = esc(p.get("description", ""))
    og_title = esc(p.get("og_title", p.get("name", "")))
    og_desc = esc(p.get("og_description", p.get("description", "")))
    og_image = esc(cfg.get("hero_image") or (cfg["images"][0]["src"] if cfg.get("images") else ""))

    email = esc_js(cfg.get("contact", {}).get("email", ""))
    prod_name = esc_js(p.get("name", ""))
    prod_sku = esc_js(p.get("sku", ""))
    prod_sku_short = esc_js(p.get("sku", "product"))

    inline_config = f"""<script>
window.__PRODUCT_CONFIG__ = {{
    email: "{email}",
    name: "{prod_name}",
    sku: "{prod_sku}"
}};
</script>"""

    json_ld = build_json_ld(cfg)
    nav = build_nav(cfg)
    hero = build_hero(cfg)
    highlights = build_highlights(cfg)
    gallery = build_gallery(cfg)
    video = build_video(cfg)
    specs = build_specifications(cfg)
    apps = build_applications(cfg)
    pkg = build_package(cfg)
    downloads = build_downloads(cfg)
    contact = build_contact(cfg)
    footer = build_footer(cfg)
    quote_modal = build_quote_modal(cfg)

    is_catalog = ROOT == os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    css_path = "../../assets/css/main.css"
    js_path = "../../assets/js/main.js"
    logo_href = "../../index.html"

    pdf_script = f"""<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js" integrity="sha512-GsLlZN/3F2ErC5ifS5QtgpiJtWd43JWSuIgh7mbzZ8zBps+dvLusV+eNQATqgA/HdeKFVgA5v3S/cIrLF7QnIg==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<script>
(function() {{
    var sku = "{prod_sku_short}";
    var btns = document.querySelectorAll(".btn-pdf");
    var filename = sku + "-catalogue.pdf";

    function generatePDF() {{
        var opt = {{
            margin:       [0.5, 0.5, 0.5, 0.5],
            filename:     filename,
            image:        {{ type: 'jpeg', quality: 0.98 }},
            html2canvas:  {{ scale: 2, letterRendering: true, useCORS: true, logging: false }},
            jsPDF:        {{ unit: 'in', format: 'a4', orientation: 'portrait' }}
        }};
        var el = document.getElementById("main");
        html2pdf().set(opt).from(el).save();
    }}

    btns.forEach(function(b) {{
        b.addEventListener("click", generatePDF);
    }});

    if (window.location.search.indexOf("dl=1") > -1) {{
        setTimeout(generatePDF, 800);
    }}
}})();
</script>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
<meta name="description" content="{meta_desc}" />
<link rel="stylesheet" href="{css_path}" />
<meta property="og:type" content="website" />
<meta property="og:title" content="{og_title}" />
<meta property="og:description" content="{og_desc}" />
<meta property="og:image" content="{og_image}" />
<script type="application/ld+json">{json_ld}</script>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>

<header class="site-header">
  <div class="wrap inner">
    <a class="logo" href="{logo_href}">{esc(p.get("sku",""))}-<span>{esc(p.get("short_name", ""))}</span></a>
    <button class="menu-toggle" id="menu-toggle" aria-label="Toggle navigation" aria-expanded="false">
      <span></span><span></span><span></span>
    </button>
    <nav class="nav" id="main-nav" aria-label="Primary">
      {nav}
    </nav>
  </div>
</header>

<main id="main">
{hero}
{highlights}
{gallery}
{video}
{specs}
{apps}
{pkg}
{downloads}
{contact}
</main>

{footer}
{quote_modal}

{inline_config}
{pdf_script}
<script src="{js_path}" defer></script>
</body>
</html>"""


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate.py <config.json>")
        print("  Output goes to products/<sku>/")
        sys.exit(1)

    config_path = sys.argv[1]
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        sys.exit(1)

    cfg = load_config(config_path)

    sku = cfg["product"].get("sku", "product")
    output_dir = os.path.join(PRODUCTS_DIR, sku)
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Create images subdir for product images
    img_dir = os.path.join(output_dir, "images")
    os.makedirs(img_dir, exist_ok=True)

    html = generate_html(cfg)
    output_path = os.path.join(output_dir, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Copy manual PDF if it exists
    manual_pdf = cfg.get("manual_pdf", "")
    if manual_pdf:
        src_pdf = os.path.join(os.path.dirname(config_path), manual_pdf)
        if os.path.exists(src_pdf):
            shutil.copy2(src_pdf, os.path.join(output_dir, os.path.basename(manual_pdf)))

    print(f"Product page generated:")
    print(f"  {output_path}")
    print(f"\nInstructions:")
    print(f"  1. Copy product images to: {img_dir}/")
    print(f"  2. Update image paths in the config JSON to: images/<filename>")
    print(f"  3. Open: file:///{output_path.replace(os.sep, '/')}")


def load_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
