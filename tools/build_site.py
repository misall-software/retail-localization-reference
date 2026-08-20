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
import posixpath
import re
import shutil
import subprocess
import sys
import datetime

try:
    import markdown
    from markdown.extensions.toc import slugify_unicode
except ImportError:
    sys.exit("markdown package required: pip install markdown")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_site")
BASE = os.environ.get("SITE_BASE", "https://misall-software.github.io/retail-localization-reference")
BASE = BASE.rstrip("/")

# Markdown file -> output path. README becomes the index of its edition.
PAGES = []

# A link to a directory in the Markdown means "the index of that edition".
# The English edition's index is the site root, because README.md is it.
DIR_INDEX = {"en": "index.html", "zh": "zh/index.html"}

# Repository files that are not pages but are linked from them. Copied to the
# site root under a name a browser will display rather than download.
ASSETS = {"LICENSE": "LICENSE.txt"}

# URLs that were linked from a published page before the site layout settled,
# and so may already be in a search index. GitHub Pages serves static files and
# cannot issue a 301, so each gets a stub that canonicalises to the real page
# and bounces the reader there. Kept out of the sitemap deliberately.
REDIRECTS = {
    "en/index.html": "index.html",      # the English edition index is the site root
    "zh/README.html": "zh/index.html",  # zh/README.md builds to zh/index.html
}


def git_date(path):
    """Date of the last commit to touch a path, as YYYY-MM-DD.

    None outside a git checkout, or when the checkout is too shallow to hold a
    commit for the path. The caller falls back to the build date, which errs
    towards re-crawling rather than towards a page looking staler than it is.
    """
    try:
        out = subprocess.check_output(["git", "log", "-1", "--format=%cs", "--", path],
                                      cwd=ROOT, stderr=subprocess.PIPE)
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.decode("ascii").strip() or None


BUILD_DATE = datetime.date.today().isoformat()

# A page is stale when its own source changes and also when the template that
# renders it changes, because a new canonical or a new nav link rewrites every
# page on the site. lastmod is what a crawler uses to decide whether re-reading
# a page is worth its time, so it has to answer both.
TEMPLATE_DATE = git_date("tools/build_site.py")


def lastmod(src):
    known = [d for d in (git_date(src), TEMPLATE_DATE) if d]
    return max(known) if known else BUILD_DATE


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


# An edition index is served both as `index.html` and as the directory holding
# it, and GitHub Pages, being static, cannot 301 one form to the other. The
# directory form is the address the repository advertises and the one inbound
# links use, so it is the canonical of the pair; `index.html` keeps working and
# carries a canonical pointing at it.
EDITION_INDEXES = {"index.html", "zh/index.html"}
INDEX = "index.html"


def canonical_url(dst):
    """Absolute URL a built page is canonical at."""
    if dst in EDITION_INDEXES:
        return BASE + "/" + dst[:-len(INDEX)]
    return BASE + "/" + dst


def link_form(rel, dst):
    """Relative link written the way canonical_url() writes the absolute one.

    Only the edition indexes differ: `../../index.html` becomes `../../`, and a
    link from the site root to itself becomes `./` rather than the empty string.
    """
    if dst not in EDITION_INDEXES:
        return rel
    return rel[:-len(INDEX)] or "./"


def out_url(src):
    for s, d, _ in PAGES:
        if s == src:
            return canonical_url(d)
    return None


def out_path(src):
    for s, d, _ in PAGES:
        if s == src:
            return d
    return None


def rewrite_links(html, src, dst):
    """Point every relative link at the file the build actually produced.

    The Markdown is read on GitHub as well as here, so its links are written
    against the repository: `zh/README.md`, `en/`, `LICENSE`. On the site those
    are `zh/index.html`, `index.html` and `LICENSE.txt`. Resolving each link
    against the repository tree and mapping it through the page table keeps one
    set of links correct in both places.

    The substitution this replaced only turned `.md` into `.html`, which quietly
    produced `zh/README.html` and left `en/` pointing at a directory with no
    index — two 404s linked from the home page, which is the page search engines
    crawl first.
    """
    srcdir = posixpath.dirname(src)
    outdir = posixpath.dirname(dst)

    def resolve(path):
        """Repository-relative target of a link, or None if it leaves the repo."""
        joined = posixpath.join(srcdir, path) if srcdir else path
        target = posixpath.normpath(joined).lstrip("/")
        return None if target == ".." or target.startswith("../") else target

    def repl(m):
        attr, href = m.group(1), m.group(2)
        # Absolute URLs, protocol-relative URLs and bare fragments are left alone.
        if re.match(r"^(?:[a-z][a-z0-9+.-]*:|//|#)", href, re.I):
            return m.group(0)
        path, hash_, frag = href.partition("#")
        if not path:
            return m.group(0)
        target = resolve(path)
        if target is None:
            return m.group(0)

        if target in ASSETS:
            out = ASSETS[target]
        elif path.endswith("/") or os.path.isdir(os.path.join(ROOT, target)):
            out = DIR_INDEX.get(target) or out_path(target + "/README.md")
        else:
            out = out_path(target)
            # data/*.json and anything else copied verbatim keeps its own path.
            if out is None and os.path.isfile(os.path.join(ROOT, target)):
                out = target
        if out is None:
            return m.group(0)  # left for check_links() to report

        # The fragment comes back out of already-escaped attribute text, so it
        # is written through unchanged rather than escaped a second time.
        rel = posixpath.relpath(out, outdir) if outdir else out
        return '%s="%s"' % (attr, link_form(rel, out) + hash_ + frag)

    return re.sub(r'\b(href|src)="([^"]*)"', repl, html)


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
        "isPartOf": {"@id": "https://github.com/misall-software/retail-localization-reference#dataset"},
        "publisher": {"@id": "https://www.misall.com/#organization"},
    })
    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      ensure_ascii=False, separators=(",", ":"))


def render(src, dst, lang):
    text = io.open(os.path.join(ROOT, src), encoding="utf-8").read()
    title = first_heading(text)
    desc = description(text)
    canonical = canonical_url(dst)
    depth = dst.count("/")
    up = "../" * depth

    # toc gives every heading an id, so a deep link such as
    # `peru.md#food-service` lands on the section it names instead of the top of
    # the page. slugify_unicode keeps Chinese headings addressable — the default
    # slugifier strips non-ASCII and would leave every zh/ heading with an empty
    # id, colliding with each other.
    html = markdown.markdown(text, extensions=["tables", "fenced_code", "attr_list",
                                               "sane_lists", "toc"],
                             extension_configs={"toc": {"slugify": slugify_unicode}})
    # Point internal links at the built pages, and wrap tables so they scroll.
    html = rewrite_links(html, src, dst)
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
        nav = '<a href="%s">Retail &amp; POS Localization Reference</a>' % (up or "./")
        if src != "README.md":
            nav += ' &middot; <a href="%ssources.html">Sources</a>' % up
        if cp and out_url(cp):
            nav += ' &middot; <a href="%s" hreflang="zh-CN">中文</a>' % out_url(cp)
        foot = ('Maintained by the MISAll team. '
                '<a href="https://github.com/misall-software/retail-localization-reference">Source on GitHub</a>. '
                'Documentation CC BY 4.0, data CC0. '
                'Nothing here is confirmed against a primary source — verify before relying on it.')
    else:
        nav = '<a href="%szh/">海外开店收银系统参考资料</a>' % up
        if cp and out_url(cp):
            nav += ' &middot; <a href="%s" hreflang="en">English</a>' % out_url(cp)
        foot = ('由秘奥软件（MISAll）团队维护。'
                '<a href="https://github.com/misall-software/retail-localization-reference">GitHub 源仓库</a>。'
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


REDIRECT_TPL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Moved &mdash; {title}</title>
<link rel="canonical" href="{canonical}">
<meta http-equiv="refresh" content="0; url={rel}">
</head>
<body>
<p>This page has moved to <a href="{rel}">{canonical}</a>.</p>
</body>
</html>
"""

NOT_FOUND_TPL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Page not found &mdash; Retail &amp; POS Localization Reference</title>
<meta name="robots" content="noindex">
<style>{css}</style>
</head>
<body>
<div class="wrap">
<h1>Page not found</h1>
<p>That address does not exist on this site. The two edition indexes are:</p>
<ul>
<li><a href="{base}/">Retail &amp; POS Localization Reference</a> &mdash; English edition</li>
<li><a href="{base}/zh/" hreflang="zh-CN">海外开店收银系统参考资料</a> &mdash; 中文版</li>
</ul>
<p>页面不存在。请从上面两个入口进入。</p>
<p><a href="{base}/sitemap.xml">sitemap.xml</a> lists every page on the site.</p>
</div>
</body>
</html>
"""


def write_redirects():
    """Stubs for URLs that were published before the layout settled."""
    for frm, to in sorted(REDIRECTS.items()):
        rel = posixpath.relpath(to, posixpath.dirname(frm)) if posixpath.dirname(frm) else to
        built = io.open(os.path.join(OUT, to), encoding="utf-8").read()
        m = re.search(r"<title>(.*?)</title>", built, re.S)
        page = REDIRECT_TPL.format(canonical=canonical_url(to), rel=link_form(rel, to),
                                   title=m.group(1).strip() if m else to)
        path = os.path.join(OUT, frm)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        io.open(path, "w", encoding="utf-8", newline="\n").write(page)
    print("  redirects -> %d stub(s)" % len(REDIRECTS))


def check_links():
    """Fail the build on a relative link that does not resolve in _site.

    Every link here is written for GitHub first and rewritten for the site
    second, so a mismatch between the two layouts shows up as a 404 on a live
    page rather than as an error at build time. This is the error at build time.
    """
    bad = []
    for dirpath, _, filenames in os.walk(OUT):
        for fn in sorted(filenames):
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            page = os.path.relpath(path, OUT).replace(os.sep, "/")
            html = io.open(path, encoding="utf-8").read()
            ids = set(re.findall(r'\bid="([^"]+)"', html))
            for href in re.findall(r'\bhref="([^"]*)"', html):
                if re.match(r"^(?:[a-z][a-z0-9+.-]*:|//)", href, re.I):
                    continue
                target, _, frag = href.partition("#")
                if not target:
                    if frag and frag not in ids:
                        bad.append("%s -> #%s (no such heading)" % (page, frag))
                    continue
                resolved = os.path.normpath(os.path.join(dirpath, target))
                if os.path.isdir(resolved):
                    resolved = os.path.join(resolved, "index.html")
                if not os.path.isfile(resolved):
                    bad.append("%s -> %s" % (page, href))
                elif frag:
                    other = io.open(resolved, encoding="utf-8").read()
                    if frag not in set(re.findall(r'\bid="([^"]+)"', other)):
                        bad.append("%s -> %s (no such heading)" % (page, href))
    if bad:
        print("broken links:")
        for b in bad:
            print("  " + b)
        sys.exit("%d broken link(s)" % len(bad))
    print("  links: all relative links resolve")


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

    urls = [(render(s, d, l), lastmod(s)) for s, d, l in PAGES]

    # data/ is served as-is so the JSON is fetchable at a stable URL.
    shutil.copytree(os.path.join(ROOT, "data"), os.path.join(OUT, "data"))

    # Files linked from the pages that are not pages. .txt rather than the bare
    # repository name so a browser shows the licence instead of downloading it.
    for name, dest in sorted(ASSETS.items()):
        shutil.copy2(os.path.join(ROOT, name), os.path.join(OUT, dest))

    write_redirects()

    # GitHub Pages serves this for any unmatched path under the project.
    io.open(os.path.join(OUT, "404.html"), "w", encoding="utf-8", newline="\n").write(
        NOT_FOUND_TPL.format(css=CSS, base=BASE))

    # static/ is copied verbatim to the site root. This is where search engine
    # ownership-verification files go — Google Search Console's HTML file, Bing's
    # BingSiteAuth.xml, an IndexNow key — so adding one is a drop-in with no code
    # change. Verifying ownership lets a sitemap be submitted directly, which is
    # what actually gets a new site crawled; an inbound link is not required.
    static = os.path.join(ROOT, "static")
    if os.path.isdir(static):
        copied = 0
        for name in sorted(os.listdir(static)):
            src = os.path.join(static, name)
            # static/README.md documents the directory for contributors; it is
            # not site content and must not be published.
            if name.upper().startswith("README"):
                continue
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(OUT, name))
                copied += 1
        print("  static/ -> %d file(s) copied to site root" % copied)

    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, lm in urls:
        # The edition indexes are the only URLs that end in a slash.
        pri = "1.0" if u.endswith("/") else "0.8"
        sm.append("<url><loc>%s</loc><lastmod>%s</lastmod>"
                  "<changefreq>monthly</changefreq><priority>%s</priority></url>" % (u, lm, pri))
    sm.append("</urlset>")
    io.open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write("\n".join(sm))

    io.open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8", newline="\n").write(
        "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % BASE)

    io.open(os.path.join(OUT, ".nojekyll"), "w", encoding="utf-8").write("")

    # Manifest of pages this script generated, for the CI check to read.
    # Written outside _site so it is never published. It exists because
    # static/ passthrough files can also be .html — a search engine
    # verification file, for instance — and those legitimately carry no
    # canonical link or JSON-LD. Checking by file extension flagged them.
    io.open(os.path.join(ROOT, "build-manifest.txt"), "w", encoding="utf-8",
            newline="\n").write("\n".join(d for _, d, _ in PAGES) + "\n")

    check_links()

    print("built %d pages -> %s" % (len(urls), OUT))
    for u, lm in urls:
        print("  ", lm, u)


if __name__ == "__main__":
    main()
