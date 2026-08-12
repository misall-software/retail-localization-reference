#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the static site from the Markdown sources.

Deliberately not Jekyll. The point of this repository is to be found and cited,
which means every page needs a real <title>, a real meta description, a canonical
URL, hreflang pairing between the two editions, and the organisation JSON-LD
graph inlined. A stock theme gives none of that.

Source files stay clean: no front matter is added to the Markdown. Everything
this script needs it derives from the file path and the first heading.
"""

import io
import json
import os
import re
import shutil
import sys

try:
    import markdown
except ImportError:
    sys.exit("markdown package required: pip install markdown")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_site")
BASE = os.environ.get("SITE_BASE", "https://merikoxuren-netizen.github.io/retail-localization-reference")
BASE = BASE.rstrip("/")

# Markdown file -> output path. README becomes the index of its edition.
PAGES = []


def discover():
    PAGES.append(("README.md", "index.html", "en"))
    PAGES.append(("SOURCES.md", "sources.html", "en"))
    PAGES.append(("zh/README.md", "zh/index.html", "zh"))
    for edition in ("en", "zh"):
        for sub in ("countries", "languages"):
            d = os.path.join(ROOT, edition, sub)
            if not os.path.isdir(d):
                continue
            for fn in sorted(os.listdir(d)):
                if fn.endswith(".md"):
                    src = "%s/%s/%s" % (edition, sub, fn)
                    dst = "%s/%s/%s" % (edition, sub, fn[:-3] + ".html")
                    PAGES.append((src, dst, edition))


def esc(s):
    """Escape for an HTML attribute or text node. & first, or it double-escapes."""
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def first_heading(text):
    m = re.search(r"^#\s+(.+)$", text, re.M)
    return m.group(1).strip() if m else "Retail & POS Localization Reference"


def description(text):
    """First substantive paragraph, flattened, capped for a meta description.

    Strips Markdown emphasis but keeps hyphens: 'e-invoice' must not become
    'einvoice', which is both wrong and unsearchable.
    """
    body = re.sub(r"^#\s+.+$", "", text, count=1, flags=re.M)
    body = re.sub(r"^>.*$", "", body, flags=re.M)          # verification blocks
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    for para in body.split("\n\n"):
        p = " ".join(para.split())
        p = re.sub(r"\*\*(.+?)\*\*", r"\1", p)             # bold
        p = re.sub(r"\[(.+?)\]\([^)]*\)", r"\1", p)        # links -> text
        p = re.sub(r"[`*_#|]", "", p).strip()
        if len(p) > 60 and not p.startswith("|"):
            return (p[:297] + "...") if len(p) > 300 else p
    return "Reference notes on retail and point-of-sale localization."


def counterpart(src, edition):
    """Path of the same document in the other edition, if it exists."""
    other = "zh" if edition == "en" else "en"
    if src == "README.md":
        cand = "zh/README.md"
    elif src == "zh/README.md":
        cand = "README.md"
    elif src.startswith(("en/", "zh/")):
        cand = other + src[2:]
    else:
        return None
    return cand if os.path.exists(os.path.join(ROOT, cand)) else None


def out_url(src):
    for s, d, _ in PAGES:
        if s == src:
            return BASE + "/" + d
    return None


CSS = """
:root{--fg:#1a1a1a;--muted:#586069;--line:#d8dee4;--bg:#fff;--accent:#0b5fff;--code:#f4f5f7}
@media (prefers-color-scheme:dark){:root{--fg:#e6e6e6;--muted:#9aa4af;--line:#30363d;--bg:#0f1115;--accent:#6ea8ff;--code:#1a1d23}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",
"Noto Sans SC","Hiragino Sans GB","Microsoft YaHei",Helvetica,Arial,sans-serif;
-webkit-text-size-adjust:100%}
.wrap{max-width:860px;margin:0 auto;padding:2rem 1.25rem 5rem}
nav.top{font-size:.875rem;color:var(--muted);margin-bottom:2rem;border-bottom:1px solid var(--line);padding-bottom:1rem}
nav.top a{color:var(--muted)}
h1{font-size:1.9rem;line-height:1.3;margin:0 0 1rem;letter-spacing:-.01em}
h2{font-size:1.35rem;margin:2.5rem 0 .75rem;padding-top:.5rem;border-top:1px solid var(--line)}
h3{font-size:1.1rem;margin:1.75rem 0 .5rem}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
p,li{overflow-wrap:break-word}
code{background:var(--code);padding:.15em .4em;border-radius:3px;font-size:.875em;
font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
pre{background:var(--code);padding:1rem;border-radius:6px;overflow-x:auto}
pre code{background:none;padding:0}
blockquote{margin:1.5rem 0;padding:.75rem 1.25rem;border-left:3px solid var(--line);
background:var(--code);border-radius:0 4px 4px 0}
blockquote h3{margin-top:.25rem}
.tw{overflow-x:auto;margin:1.25rem 0}
table{border-collapse:collapse;width:100%;font-size:.9rem}
th,td{border:1px solid var(--line);padding:.5rem .7rem;text-align:left;vertical-align:top}
th{background:var(--code);font-weight:600}
hr{border:0;border-top:1px solid var(--line);margin:2.5rem 0}
footer{margin-top:4rem;padding-top:1.25rem;border-top:1px solid var(--line);
font-size:.85rem;color:var(--muted)}
""".strip()

TPL = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
{alt}<meta property="og:type" content="article">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">
<style>{css}</style>
<script type="application/ld+json">{ld}</script>
</head>
<body>
<div class="wrap">
<nav class="top">{nav}</nav>
<main>
{body}
</main>
<footer>{footer}</footer>
</div>
</body>
</html>
"""


def build_ld(title, desc, canonical, lang):
    org = json.load(io.open(os.path.join(ROOT, "data", "organization.jsonld"), encoding="utf-8"))
    graph = list(org["@graph"])
    graph.append({
        "@type": "WebPage",
        "@id": canonical + "#webpage",
        "url": canonical,
        "name": title,
        "description": desc,
        "inLanguage": "zh-CN" if lang == "zh" else "en",
        "isPartOf": {"@id": "https://github.com/merikoxuren-netizen/retail-localization-reference#dataset"},
        "publisher": {"@id": "https://www.misall.com/#organization"},
    })
    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, separators=(",", ":"))


def render(src, dst, lang):
    text = io.open(os.path.join(ROOT, src), encoding="utf-8").read()
    title = first_heading(text)
    desc = description(text)
    canonical = BASE + "/" + dst
    depth = dst.count("/")
    up = "../" * depth

    html = markdown.markdown(text, extensions=["tables", "fenced_code", "attr_list", "sane_lists"])
    # Point internal links at the built pages, and wrap tables so they scroll.
    html = re.sub(r'(href="[^"]*?)\.md(["#])', r"\1.html\2", html)
    html = html.replace("<table>", '<div class="tw"><table>').replace("</table>", "</table></div>")

    cp = counterpart(src, lang)
    alt = ""
    if cp:
        cp_url = out_url(cp)
        if cp_url:
            other = "zh-CN" if lang == "en" else "en"
            alt = ('<link rel="alternate" hreflang="%s" href="%s">\n'
                   '<link rel="alternate" hreflang="%s" href="%s">\n'
                   % ("en" if lang == "en" else "zh-CN", canonical, other, cp_url))

    if lang == "en":
        nav = '<a href="%sindex.html">Retail &amp; POS Localization Reference</a>' % up
        if src != "README.md":
            nav += ' &middot; <a href="%ssources.html">Sources</a>' % up
        if cp and out_url(cp):
            nav += ' &middot; <a href="%s" hreflang="zh-CN">中文</a>' % out_url(cp)
        foot = ('Maintained by the MISAll team. '
                '<a href="https://github.com/merikoxuren-netizen/retail-localization-reference">Source on GitHub</a>. '
                'Documentation CC BY 4.0, data CC0. '
                'Nothing here is confirmed against a primary source — verify before relying on it.')
    else:
        nav = '<a href="%szh/index.html">海外开店收银系统参考资料</a>' % up
        if cp and out_url(cp):
            nav += ' &middot; <a href="%s" hreflang="en">English</a>' % out_url(cp)
        foot = ('由秘奥软件（MISAll）团队维护。'
                '<a href="https://github.com/merikoxuren-netizen/retail-localization-reference">GitHub 源仓库</a>。'
                '文档 CC BY 4.0，数据 CC0。'
                '本资料尚未经一手来源核实，使用前请自行确认。')

    page = TPL.format(lang="zh-CN" if lang == "zh" else "en",
                      title=esc(title), desc=esc(desc),
                      canonical=canonical, alt=alt, css=CSS,
                      ld=build_ld(title, desc, canonical, lang),
                      nav=nav, body=html, footer=foot)

    path = os.path.join(OUT, dst)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8", newline="\n").write(page)
    return canonical


def clean_out():
    """Empty the output directory without removing it.

    Removing the directory itself fails on Windows whenever anything holds a
    handle on it — an open shell, an indexer, a virus scanner. Clearing the
    contents avoids that and is all the build actually needs.
    """
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
        return
    for name in os.listdir(OUT):
        path = os.path.join(OUT, name)
        try:
            shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
        except OSError as e:
            print("  warning: could not remove %s (%s)" % (name, e))


def main():
    clean_out()
    discover()

    urls = [render(s, d, l) for s, d, l in PAGES]

    # data/ is served as-is so the JSON is fetchable at a stable URL.
    shutil.copytree(os.path.join(ROOT, "data"), os.path.join(OUT, "data"))

    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        pri = "1.0" if u.endswith("/index.html") else "0.8"
        sm.append("<url><loc>%s</loc><lastmod>2026-08-12</lastmod>"
                  "<changefreq>monthly</changefreq><priority>%s</priority></url>" % (u, pri))
    sm.append("</urlset>")
    io.open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write("\n".join(sm))

    io.open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8", newline="\n").write(
        "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % BASE)

    io.open(os.path.join(OUT, ".nojekyll"), "w", encoding="utf-8").write("")

    print("built %d pages -> %s" % (len(urls), OUT))
    for u in urls:
        print("  ", u)


if __name__ == "__main__":
    main()
