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
    if text is None:
        return ""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def esc_js(text):
    if text is None:
        return ""
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'").replace("\n", "\\n").replace("\r", "")

def t(val):
    """Generate bilingual span for a value that may be string or {en, zh}."""
    if isinstance(val, dict) and "en" in val and "zh" in val:
        return '<span lang="en">' + esc(val["en"]) + '</span><span lang="zh" hidden>' + esc(val["zh"]) + '</span>'
    return esc(val)

def t_flat(val, lang="en"):
    """Extract a single language from a bilingual value."""
    if isinstance(val, dict) and lang in val:
        return esc(val[lang])
    return esc(val)


def build_json_ld(cfg):
    p = cfg["product"]
    images = cfg.get("images", [])
    img_list = json.dumps([img.get("src", "") for img in images])
    name_en = t_flat(p.get("name", ""), "en")
    desc_en = t_flat(p.get("description", ""), "en")
    return f"""{{
        "@context": "https://schema.org",
        "@type": "Product",
        "name": {json.dumps(name_en)},
        "sku": {json.dumps(p.get("sku",""))},
        "description": {json.dumps(desc_en)},
        "brand": {{ "@type": "Brand", "name": {json.dumps(p.get("brand",""))} }},
        "image": {img_list},
        "manufacturer": {{
            "@type": "Organization",
            "name": {json.dumps(p.get("manufacturer",""))}
        }}
    }}"""


def build_nav(cfg):
    has_video = bool(cfg.get("videos", [])) or bool(cfg.get("video", {}).get("available", False))
    pairs = [
        ("../../index.html", "Catalog", "产品目录"),
        ("#overview", "Overview", "产品概览"),
        ("#highlights", "Highlights", "产品亮点"),
        ("#gallery", "Gallery", "产品图库"),
    ]
    if has_video:
        pairs.append(("#video", "Video", "产品视频"))
    pairs += [
        ("#specifications", "Specifications", "技术参数"),
        ("#applications", "Applications", "应用场景"),
        ("#package", "Package", "包装清单"),
        ("#downloads", "Downloads", "资料下载"),
        ("#contact", "Contact", "联系我们"),
    ]
    return "".join(
        f'<a href="{href}"><span lang="en">{en}</span><span lang="zh" hidden>{zh}</span></a>'
        for href, en, zh in pairs
    )


DOC_CATEGORIES = ["全部", "用户手册", "规格书", "使用说明", "支持文档", "操作指引"]
VIDEO_CATEGORIES = ["全部", "产品概览", "使用说明", "安装指引", "操作演示", "其他"]
DOC_FORMATS = {"pdf":"PDF","png":"图片","jpg":"图片","jpeg":"图片","gif":"图片","webp":"图片","doc":"WORD","docx":"WORD","xls":"EXCEL","xlsx":"EXCEL","md":"MARKDOWN","markdown":"MARKDOWN"}

BILINGUAL_CATS = {
    "全部": "All", "主图": "Main", "细节": "Detail", "其他": "Other",
    "用户手册": "User Manual", "规格书": "Specification",
    "使用说明": "Instructions", "支持文档": "Support", "操作指引": "Guide",
    "产品概览": "Overview", "安装指引": "Installation", "操作演示": "Demo"
}

def biling_btn(text, active=False, extra_attrs=""):
    """Generate a bilingual button with lang spans."""
    en = BILINGUAL_CATS.get(text, text)
    active_cls = ' class="is-active"' if active else ''
    return f'<button type="button"{active_cls} data-cat="{esc(text)}"{extra_attrs}><span lang="en">{esc(en)}</span><span lang="zh" hidden>{esc(text)}</span></button>\n'

def doc_format(filepath):
    ext = os.path.splitext(filepath)[1].lstrip(".").lower()
    return DOC_FORMATS.get(ext, ext.upper())

def build_docs_dropdown(cfg):
    documents = cfg.get("documents", [])
    manual_pdf = cfg.get("manual_pdf", "")
    if manual_pdf:
        has_manual = any(d.get("file","") == manual_pdf for d in documents)
        if not has_manual:
            documents = [{"label": "User Manual (PDF)", "file": manual_pdf, "category": "用户手册"}] + documents
    count = len(documents)
    items = "".join(
        f'<a class="docs-dropdown__item" href="{esc(d["file"])}" download="{esc(os.path.basename(d["file"]))}">{esc(d["label"])}</a>\n'
        for d in documents
    )
    html = f"""<div class="docs-dropdown">
  <button type="button" class="btn btn-primary btn-docs" data-docs-toggle id="hero-docs-btn"><span lang="en">Data Download</span><span lang="zh" hidden>资料下载</span> <span class="doc-count" id="hero-docs-count">({count})</span> &#9660;</button>
  <div class="docs-dropdown__menu" id="hero-docs-menu" hidden>
    {items}  </div>
</div>"""
    return html, " for technical documentation"

def build_hero(cfg):
    p = cfg["product"]
    hero_img = cfg.get("hero_image") or cfg["images"][0]["src"]
    manual_pdf = cfg.get("manual_pdf", "")
    dl = os.path.basename(manual_pdf) if manual_pdf else ""
    page_num = p.get("page_number", 1)
    docs_dropdown, docs_suffix = build_docs_dropdown(cfg)
    doc_note_en = "For technical support or customized OEM versions, email us from <a href=\"#contact\">Contact Information</a>."
    doc_note_zh = "如需技术支持或定制OEM版本，请通过<a href=\"#contact\">联系方式</a>发送邮件。"
    return f"""<section class="hero wrap" id="overview">
  <div class="hero-grid">
    <div>
      <div class="page-badge"><span lang="en">Page {page_num}</span><span lang="zh" hidden>第 {page_num} 页</span></div>
      <h1>{t(p.get("name",""))}</h1>
      <p class="lead">{t(p.get("lead",""))}</p>
      <div class="hero-actions">
        <button type="button" class="btn btn-primary btn-pdf"><span lang="en">Print</span><span lang="zh" hidden>打印</span></button>
        {docs_dropdown}
        <button type="button" class="btn btn-secondary" id="quote-open-btn" data-open-quote><span lang="en">Request Quote</span><span lang="zh" hidden>获取报价</span></button>
      </div>
      <p class="doc-note"><span lang="en">{doc_note_en}</span><span lang="zh" hidden>{doc_note_zh}</span>{docs_suffix}</p>
    </div>
    <div class="hero-visual">
      <img src="{esc(hero_img)}" alt="{t_flat(p.get("name",""))}" width="800" height="800" fetchpriority="high" />
    </div>
  </div>
</section>"""


def build_highlights(cfg):
    items = cfg.get("highlights", [])
    if not items:
        return ""
    cards = "".join(
        f'<div class="card"><h3>{t(item["title"])}</h3><p>{t(item["text"])}</p></div>\n'
        for item in items
    )
    return f"""<section class="wrap" id="highlights">
  <h2 class="section-title"><span lang="en">Key Highlights</span><span lang="zh" hidden>产品亮点</span></h2>
  <p class="section-sub"><span lang="en">Precision monitoring meets rugged industrial design.</span><span lang="zh" hidden>精准监测与工业级设计相结合。</span></p>
  <div class="highlights">
    {cards}
  </div>
</section>"""


def build_gallery(cfg):
    images = cfg.get("images", [])
    has_content = bool(images)
    gallery_cats = ["全部", "主图", "细节", "其他"]
    tabs = ""
    for i, cat in enumerate(gallery_cats):
        tabs += biling_btn(cat, active=(i==0))
    thumbs = ""
    if has_content:
        first_active = True
        for img in images:
            src = esc(img.get("src", ""))
            alt = esc(img.get("alt", ""))
            cat = esc(img.get("category", "其他"))
            cls = "gthumb" + (" is-active" if first_active else "")
            first_active = False
            cat_en = BILINGUAL_CATS.get(cat, cat)
            thumbs += f"""<button type="button" class="{cls}" data-full="{src}" data-alt="{alt}" data-category="{cat}"><img src="{src}" alt="" width="120" height="90" loading="lazy" /><span class="thumb-cat"><span lang="en">{esc(cat_en)}</span><span lang="zh" hidden>{esc(cat)}</span></span></button>\n"""
    return f"""<section class="wrap" id="gallery">
  <h2 class="section-title"><span lang="en">Product Gallery</span><span lang="zh" hidden>产品图库</span></h2>
  <p class="section-sub"><span lang="en">Detailed views of the product.</span><span lang="zh" hidden>产品详细视图。</span></p>
  <div class="gallery-toolbar" id="gallery-toolbar"{' hidden' if not has_content else ''}>
    <div class="gallery-cats" id="gallery-cats">
      {tabs}
    </div>
    <div class="gallery-actions">
      <button type="button" class="btn btn-sm" id="gallery-edit-btn"><span lang="en">Edit Gallery</span><span lang="zh" hidden>编辑图库</span></button>
      <button type="button" class="btn btn-sm btn-primary" id="gallery-save-btn" hidden><span lang="en">Save Changes</span><span lang="zh" hidden>保存修改</span></button>
    </div>
  </div>
  <div class="module-empty" id="gallery-empty"{' hidden' if has_content else ''}>
    <p class="module-empty-text"><span lang="en">Pending upload</span><span lang="zh" hidden>待上传</span></p>
  </div>
  <div class="gallery-layout gallery-layout--v2" id="gallery-content"{' hidden' if not has_content else ''}>
    <div class="stage" id="gallery-stage" aria-live="polite"></div>
    <div class="thumbs" id="gallery-thumbs" role="tablist" aria-label="Gallery thumbnails">
      {thumbs}
    </div>
  </div>
  <input type="file" id="gallery-file-input" accept="image/*" multiple style="display:none" />
</section>"""

def gallery_script(cfg):
    images = cfg.get("images", [])
    data = []
    for img in images:
        data.append({
            "src": img.get("src", ""),
            "alt": img.get("alt", ""),
            "category": img.get("category", "其他")
        })
    return f"""<script id="gallery-data" type="application/json">{json.dumps(data)}</script>"""


def build_videos(cfg):
    videos = cfg.get("videos", [])
    old_video = cfg.get("video", {})
    if old_video.get("available") and not videos:
        videos = [{"label": "Product Video", "file": old_video["src"], "poster": old_video.get("poster",""), "category": "产品概览"}]
    has_content = bool(videos)
    for v in videos:
        if "category" not in v:
            v["category"] = "产品概览"
    vid_cats = VIDEO_CATEGORIES[1:]
    cat_html = ""
    for cat in vid_cats:
        cat_vids = [v for v in videos if v.get("category") == cat]
        if not cat_vids:
            continue
        items = ""
        for i, v in enumerate(cat_vids, 1):
            poster = esc(v.get("poster", ""))
            src = esc(v["file"])
            label = esc(v.get("label", ""))
            items += f"""<li class="vlist-item" data-src="{src}" data-poster="{poster}" data-label="{label}" data-category="{esc(cat)}">
  <span class="vlist-num">{i}</span>
  <span class="vlist-label">{label}</span>
</li>\n"""
        cat_en = BILINGUAL_CATS.get(cat, cat)
        cat_html += f"""<ul class="vlist-group" data-category="{esc(cat)}">
  <li class="vlist-group-header"><span lang="en">{esc(cat_en)}</span><span lang="zh" hidden>{esc(cat)}</span></li>
  {items}</ul>\n"""
    tabs = ""
    for i, cat in enumerate(VIDEO_CATEGORIES):
        tabs += biling_btn(cat, active=(i==0))
    return f"""<section class="wrap" id="video">
  <h2 class="section-title"><span lang="en">Videos</span><span lang="zh" hidden>产品视频</span></h2>
  <p class="section-sub"><span lang="en">Product videos and demonstrations.</span><span lang="zh" hidden>产品视频与演示。</span></p>
  <div class="video-toolbar" id="video-toolbar"{' hidden' if not has_content else ''}>
    <div class="video-cats" id="video-cats">
      {tabs}
    </div>
    <div class="video-actions">
      <button type="button" class="btn btn-sm" id="video-edit-btn"><span lang="en">Edit Videos</span><span lang="zh" hidden>编辑视频</span></button>
      <button type="button" class="btn btn-sm btn-primary" id="video-save-btn" hidden><span lang="en">Save Changes</span><span lang="zh" hidden>保存修改</span></button>
    </div>
  </div>
  <div class="module-empty" id="video-empty"{' hidden' if has_content else ''}>
    <p class="module-empty-text"><span lang="en">Pending upload</span><span lang="zh" hidden>待上传</span></p>
  </div>
  <div class="video-area" id="video-content"{' hidden' if not has_content else ''}>
    <div class="video-player-wrap">
      <video class="video-player" id="video-player" controls preload="metadata"></video>
      <p class="video-placeholder" id="video-placeholder"><span lang="en">Select a video to play</span><span lang="zh" hidden>选择一个视频播放</span></p>
    </div>
    <div class="video-list" id="video-list">
      {cat_html}
    </div>
  </div>
  <input type="file" id="video-file-input" accept="video/mp4,video/webm,video/ogg" multiple style="display:none" />
</section>"""

def build_video_script(cfg):
    videos = cfg.get("videos", [])
    old_video = cfg.get("video", {})
    if old_video.get("available") and not videos:
        videos = [{"label": "Product Video", "file": old_video["src"], "poster": old_video.get("poster",""), "category": "产品概览"}]
    data = []
    for v in videos:
        data.append({
            "label": v.get("label", ""),
            "file": v["file"],
            "poster": v.get("poster", ""),
            "category": v.get("category", "产品概览")
        })
    return f"""<script id="video-data" type="application/json">{json.dumps(data)}</script>"""


def build_specifications(cfg):
    specs = cfg.get("specifications", [])
    if not specs:
        return ""
    rows = "".join(
        f'<tr><th scope="row">{t(s["label"])}</th><td>{t(s["value"])}</td></tr>\n'
        for s in specs
    )
    return f"""<section class="wrap" id="specifications">
  <h2 class="section-title"><span lang="en">Specifications</span><span lang="zh" hidden>技术参数</span></h2>
  <p class="section-sub"><span lang="en">Technical parameters based on the product manual.</span><span lang="zh" hidden>基于产品手册的技术参数。</span></p>
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
        f'<div class="card"><h3>{t(a["title"])}</h3><p>{t(a["text"])}</p></div>\n'
        for a in apps
    )
    return f"""<section class="wrap" id="applications">
  <h2 class="section-title"><span lang="en">Typical Applications</span><span lang="zh" hidden>典型应用场景</span></h2>
  <p class="section-sub"><span lang="en">Optimized for diverse agricultural and environmental monitoring needs.</span><span lang="zh" hidden>适用于多种农业和环境监测需求。</span></p>
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
        rows += f"<tr><td>{i}</td><td>{t(item['item'])}</td><td>{esc(str(item['qty']))}</td></tr>\n"
    return f"""<section class="wrap" id="package">
  <h2 class="section-title"><span lang="en">Standard Package</span><span lang="zh" hidden>标准包装</span></h2>
  <p class="section-sub"><span lang="en">Standard configuration for the product.</span><span lang="zh" hidden>产品的标准配置。</span></p>
  <div class="spec-table-wrap">
    <table class="spec">
      <thead>
        <tr><th scope="col">#</th><th scope="col"><span lang="en">Item</span><span lang="zh" hidden>名称</span></th><th scope="col"><span lang="en">Qty</span><span lang="zh" hidden>数量</span></th></tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
  </div>
</section>"""


def build_downloads(cfg):
    documents = cfg.get("documents", [])
    manual_pdf = cfg.get("manual_pdf", "")
    if manual_pdf:
        has_manual = any(d.get("file","") == manual_pdf for d in documents)
        if not has_manual:
            documents = [{"label": "User Manual (PDF)", "file": manual_pdf, "category": "用户手册"}] + documents
    has_content = bool(documents)
    doc_cats = DOC_CATEGORIES[1:]
    for d in documents:
        if "category" not in d:
            d["category"] = "支持文档"
    cat_html = ""
    for cat in doc_cats:
        cat_docs = [d for d in documents if d.get("category") == cat]
        if not cat_docs:
            continue
        rows = ""
        for i, d in enumerate(cat_docs, 1):
            fmt = doc_format(d["file"])
            fn = os.path.basename(d["file"])
            rows += f"""<tr class="doc-row" data-category="{esc(cat)}">
  <td class="doc-num">{i}</td>
  <td class="doc-fmt"><span class="doc-badge badge-{fmt.lower()}">{fmt}</span></td>
  <td class="doc-name"><a class="dl-link" href="{esc(d["file"])}" download="{esc(fn)}">{esc(d["label"])}</a></td>
  <td class="doc-action"></td>
</tr>\n"""
        cat_en = BILINGUAL_CATS.get(cat, cat)
        cat_html += f"""<tbody class="doc-group" data-category="{esc(cat)}">
  <tr class="doc-group-header"><td colspan="4"><span lang="en">{esc(cat_en)}</span><span lang="zh" hidden>{esc(cat)}</span></td></tr>
  {rows}</tbody>\n"""
    docs_toolbar_hidden = ' hidden' if not has_content else ''
    docs_empty_hidden = '' if not has_content else ' hidden'
    docs_content_hidden = ' hidden' if not has_content else ''
    return f"""<section class="wrap" id="downloads">
  <h2 class="section-title"><span lang="en">Downloads</span><span lang="zh" hidden>资料下载</span></h2>
  <p class="section-sub"><span lang="en">Access technical documentation for the product.</span><span lang="zh" hidden>获取产品的技术文档。</span></p>
  <div class="doc-toolbar" id="doc-toolbar"{docs_toolbar_hidden}>
    <div class="doc-cats" id="doc-cats">
      {biling_btn("全部", active=True)}
      {biling_btn("用户手册")}
      {biling_btn("规格书")}
      {biling_btn("使用说明")}
      {biling_btn("支持文档")}
      {biling_btn("操作指引")}
    </div>
    <div class="doc-toolbar-actions">
      <button type="button" class="btn btn-sm" id="doc-edit-btn"><span lang="en">Edit Docs</span><span lang="zh" hidden>编辑文档</span></button>
      <button type="button" class="btn btn-sm btn-primary" id="doc-save-btn" hidden><span lang="en">Save Changes</span><span lang="zh" hidden>保存修改</span></button>
    </div>
  </div>
  <div class="module-empty" id="doc-empty"{docs_empty_hidden}>
    <p class="module-empty-text"><span lang="en">Pending upload</span><span lang="zh" hidden>待上传</span></p>
  </div>
  <div class="doc-table-wrap" id="doc-content"{docs_content_hidden}>
    <table class="doc-table" id="doc-table">
      {cat_html}
    </table>
  </div>
  <input type="file" id="doc-file-input" accept=".pdf,.png,.jpg,.jpeg,.doc,.docx,.xls,.xlsx,.md" multiple style="display:none" />
</section>"""

def build_doc_script(cfg):
    documents = cfg.get("documents", [])
    manual_pdf = cfg.get("manual_pdf", "")
    if manual_pdf:
        has_manual = any(d.get("file","") == manual_pdf for d in documents)
        if not has_manual:
            documents = [{"label": "User Manual (PDF)", "file": manual_pdf, "category": "用户手册"}] + documents
    data = []
    for d in documents:
        fmt = doc_format(d["file"])
        cat = d.get("category") or "支持文档"
        data.append({
            "label": d["label"],
            "file": d["file"],
            "category": cat,
            "format": fmt
        })
    return f"""<script id="doc-data" type="application/json">{json.dumps(data)}</script>"""


def build_contact(cfg):
    c = cfg.get("contact", {})
    return f"""<section class="wrap" id="contact">
  <h2 class="section-title"><span lang="en">Contact Information</span><span lang="zh" hidden>联系方式</span></h2>
  <p class="section-sub"><span lang="en">For quotations, lead times, and technical support.</span><span lang="zh" hidden>获取报价、交期和技术支持。</span></p>
  <address class="contact-info">
    {c.get("address","")}<br />
    <a href="tel:{esc(c.get("phone",""))}">{esc(c.get("phone",""))}</a><br />
    <a href="mailto:{esc(c.get("email",""))}">{esc(c.get("email",""))}</a><br />
    <span lang="en">{esc(c.get("hours",""))}</span><span lang="zh" hidden>周一至周五，9:00 - 18:00</span>
  </address>
</section>"""


def build_footer(cfg):
    p = cfg["product"]
    page_num = p.get("page_number", 1)
    return f"""<footer class="site-footer">
  <div class="wrap footer-meta">
    <span>{t(p.get("manufacturer",""))} &middot; SKU {esc(p.get("sku",""))}</span>
    <span><span lang="en">Page {page_num} &middot; Product Catalogue</span><span lang="zh" hidden>第 {page_num} 页 &middot; 产品目录</span></span>
  </div>
</footer>"""


def build_quote_modal(cfg):
    p = cfg["product"]
    return f"""<div class="quote-modal" id="quote-modal" role="dialog" aria-modal="true" aria-labelledby="quote-modal-title" aria-hidden="true">
  <div class="quote-modal__backdrop" data-close-quote tabindex="-1"></div>
  <div class="quote-modal__dialog">
    <h2 class="quote-modal__title" id="quote-modal-title"><span lang="en">Request a quote</span><span lang="zh" hidden">获取报价</span></h2>
    <p class="quote-modal__lead">{t(p.get("name",""))} - <span lang="en">Tell us about your project.</span><span lang="zh" hidden">告诉我们您的项目需求。</span></p>
    <form class="quote-form" id="quote-form" novalidate>
      <div class="quote-form__row">
        <label for="quote-name"><span lang="en">Full name</span><span lang="zh" hidden>姓名</span> <span aria-hidden="true">*</span></label>
        <input id="quote-name" name="name" type="text" autocomplete="name" required maxlength="120" />
      </div>
      <div class="quote-form__row">
        <label for="quote-company"><span lang="en">Company</span><span lang="zh" hidden">公司</span> <span aria-hidden="true">*</span></label>
        <input id="quote-company" name="company" type="text" autocomplete="organization" required maxlength="160" />
      </div>
      <div class="quote-form__row quote-form__row--half">
        <div>
          <label for="quote-email"><span lang="en">Work email</span><span lang="zh" hidden">工作邮箱</span> <span aria-hidden="true">*</span></label>
          <input id="quote-email" name="email" type="email" autocomplete="email" required maxlength="120" />
        </div>
        <div>
          <label for="quote-phone"><span lang="en">Phone</span><span lang="zh" hidden">电话</span></label>
          <input id="quote-phone" name="phone" type="tel" autocomplete="tel" maxlength="40" />
        </div>
      </div>
      <div class="quote-form__row">
        <label for="quote-region"><span lang="en">Country / region</span><span lang="zh" hidden">国家/地区</span> <span aria-hidden="true">*</span></label>
        <input id="quote-region" name="region" type="text" autocomplete="country-name" required maxlength="80" />
      </div>
      <div class="quote-form__row">
        <label for="quote-message"><span lang="en">Application notes</span><span lang="zh" hidden">应用说明</span> <span aria-hidden="true">*</span></label>
        <textarea id="quote-message" name="message" rows="4" required maxlength="2000" placeholder="Sensor types, network requirements, project scope..."></textarea>
      </div>
      <p class="quote-form__hint" id="quote-form-hint" role="status" aria-live="polite"></p>
      <div class="quote-form__actions">
        <button type="button" class="btn btn-secondary" data-close-quote><span lang="en">Cancel</span><span lang="zh" hidden>取消</span></button>
        <button type="submit" class="btn btn-primary"><span lang="en">Send</span><span lang="zh" hidden>发送</span></button>
      </div>
    </form>
    <button type="button" class="quote-modal__close" data-close-quote aria-label="Close dialog">&times;</button>
  </div>
</div>"""


def generate_html(cfg):
    p = cfg["product"]
    name_en = t_flat(p.get("name", ""), "en")
    name_zh = t_flat(p.get("name", ""), "zh")
    desc_en = t_flat(p.get("description", ""), "en")
    title = name_en + " | " + esc(p.get("sku",""))
    meta_desc = desc_en
    og_title = name_en
    og_desc = t_flat(p.get("og_description", desc_en), "en")
    og_image = esc(cfg.get("hero_image") or (cfg["images"][0]["src"] if cfg.get("images") else ""))

    email = esc_js(cfg.get("contact", {}).get("email", ""))
    prod_sku = esc_js(p.get("sku", ""))
    prod_sku_short = esc_js(p.get("sku", "product"))

    inline_config = f"""<script>
window.__PRODUCT_CONFIG__ = {{
    email: "{email}",
    name: "{esc_js(name_en)}",
    sku: "{prod_sku}"
}};
</script>"""

    json_ld = build_json_ld(cfg)
    nav = build_nav(cfg)
    hero = build_hero(cfg)
    highlights = build_highlights(cfg)
    gallery = build_gallery(cfg)
    gallery_data_script = gallery_script(cfg)
    videos = build_videos(cfg)
    video_data_script = build_video_script(cfg)
    specs = build_specifications(cfg)
    apps = build_applications(cfg)
    pkg = build_package(cfg)
    downloads = build_downloads(cfg)
    doc_data_script = build_doc_script(cfg)
    contact = build_contact(cfg)
    footer = build_footer(cfg)
    quote_modal = build_quote_modal(cfg)

    is_catalog = ROOT == os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    css_path = "../../assets/css/main.css"
    js_path = "../../assets/js/main.js"
    logo_href = "../../index.html"

    i18n_script = """<script>
var currentLang = "en";
function applyLang(lang) {
  currentLang = lang;
  document.querySelectorAll("[lang]").forEach(function(el) {
    if (el.tagName === "HTML") return;
    el.hidden = el.getAttribute("lang") !== lang;
  });
  var tb = document.getElementById("lang-toggle");
  if (tb) tb.textContent = lang === "en" ? "中 / EN" : "EN / 中";
}
document.addEventListener("DOMContentLoaded", function() {
  applyLang("en");
  var tb = document.getElementById("lang-toggle");
  if (tb) tb.addEventListener("click", function() { applyLang(currentLang === "en" ? "zh" : "en"); });
});
</script>"""

    pdf_script = """<script>
(function() {
    var btns = document.querySelectorAll(".btn-pdf");

    function printPage() {
        window.print();
    }

    btns.forEach(function(b) {
        b.addEventListener("click", printPage);
    });

    if (window.location.search.indexOf("dl=1") > -1) {
        setTimeout(printPage, 600);
    }

    // Document dropdown toggle
    var docTriggers = document.querySelectorAll("[data-docs-toggle]");
    docTriggers.forEach(function(btn) {
        btn.addEventListener("click", function(e) {
            e.stopPropagation();
            var menu = btn.parentElement.querySelector(".docs-dropdown__menu");
            if (menu) {
                var isOpen = !menu.hasAttribute("hidden");
                menu.hidden = isOpen;
                var base = btn.innerHTML.replace(/[▼▲].*/, "").trim();
                btn.innerHTML = isOpen ? base + " &#9650;" : base + " &#9660;";
            }
        });
    });
    document.addEventListener("click", function() {
        document.querySelectorAll(".docs-dropdown__menu:not([hidden])").forEach(function(m) {
            m.hidden = true;
            var btn = m.parentElement.querySelector("[data-docs-toggle]");
            if (btn) btn.innerHTML = btn.innerHTML.replace(/[▲▼].*/, "").trim() + " &#9660;";
        });
    });
})();
</script>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title lang="en">{title}</title><title lang="zh" hidden>{esc(name_zh)} | {esc(p.get("sku",""))}</title>
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
    <a class="logo" href="{logo_href}"><span>{esc(p.get("sku",""))}</span></a>
    <div class="header-right">
      <button type="button" class="lang-toggle" id="lang-toggle" title="Switch language">中 / EN</button>
      <button class="menu-toggle" id="menu-toggle" aria-label="Toggle navigation" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
    </div>
    <nav class="nav" id="main-nav" aria-label="Primary">
      {nav}
    </nav>
  </div>
</header>

<main id="main">
{hero}
{highlights}
{gallery}
{videos}
{specs}
{apps}
{pkg}
{downloads}
{contact}
</main>

{footer}
{quote_modal}

{inline_config}
{gallery_data_script}
{video_data_script}
{doc_data_script}
{i18n_script}
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
