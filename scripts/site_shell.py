"""Shared site shell: <head> links, navigation and footer for every page.

Every builder calls ``apply_shell`` as its final step so the navigation and the
footer live in exactly one place. ``prefix`` is the path back to the site root
("" for root pages, "../" for pages in benchmark/ or tasks/).
"""
import re

REPO = 'https://github.com/KKUN616826/preview-7k4-r9m2'
ASSET_VERSION = 'ds-20261104'

GITHUB_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M12 .5a11.5 11.5 0 0 0-3.64 22.41c.58.1.79-.25.79-.56v-2c-3.2.7-3.88-1.37-3.88-1.37-.53-1.33-1.28-1.69-1.28-1.69-1.05-.71.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.77 2.7 1.26 3.36.96.1-.75.4-1.26.73-1.55-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.17 1.18a11 11 0 0 1 5.77 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.84 1.19 3.1 0 4.42-2.7 5.39-5.26 5.68.41.36.78 1.06.78 2.14v3.17c0 .31.21.67.8.56A11.5 11.5 0 0 0 12 .5Z"/></svg>')
MENU_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'

NAV = [
    ('leaderboard', 'leaderboard.html', 'Leaderboard'),
    ('benchmark', 'benchmark.html', 'Benchmark'),
    ('docs', 'resources.html', 'Docs'),
]


def head_links(prefix=''):
    v = ASSET_VERSION
    return (
        f'<link rel="preload" href="{prefix}media/fonts/inter/Inter-latin-wght.woff2" as="font" type="font/woff2" crossorigin>'
        f'<link rel="stylesheet" href="{prefix}media/tokens.css?v={v}">'
        f'<link rel="stylesheet" href="{prefix}media/components.css?v={v}">'
    )


def header(current='', prefix='', main_id='main'):
    links = ''.join(
        f'<a href="{prefix}{href}"' + (' aria-current="page"' if key == current else '') + f'>{label}</a>'
        for key, href, label in NAV
    )
    links += f'<a class="site-links-submit" href="{prefix}leaderboard.html#submit">Submit a model</a>'
    return (
        f'<a class="skip-link" href="#{main_id}">Skip to content</a>'
        '<header class="site-header"><nav class="site-nav" aria-label="Main">'
        f'<a class="site-logo" href="{prefix}index.html" aria-label="Mind2Act World home">'
        f'<img src="{prefix}media/images/mind2act-nav-world.svg?v=33" alt="Mind2Act World" width="132" height="40"></a>'
        f'<div class="site-links" id="siteLinks">{links}</div>'
        '<div class="site-actions">'
        f'<a class="icon-btn" href="{REPO}" target="_blank" rel="noopener" aria-label="Source code on GitHub">{GITHUB_SVG}</a>'
        f'<a class="btn btn-primary btn-sm" href="{prefix}leaderboard.html#submit">Submit</a>'
        f'<button class="icon-btn site-menu" type="button" aria-expanded="false" aria-controls="siteLinks" aria-label="Open menu">{MENU_SVG}</button>'
        '</div></nav></header>'
        '<script>(()=>{const b=document.querySelector(".site-menu"),l=document.getElementById("siteLinks");'
        'if(!b||!l)return;b.addEventListener("click",()=>{const o=l.classList.toggle("is-open");b.setAttribute("aria-expanded",o);'
        'b.setAttribute("aria-label",o?"Close menu":"Open menu")});})();</script>'
    )


def footer(prefix=''):
    return (
        '<footer class="site-footer"><div class="container">'
        '<div class="footer-grid">'
        f'<div><img src="{prefix}media/images/mind2act-nav-world.svg?v=33" alt="Mind2Act World" width="150" height="45">'
        '<p>A simulation benchmark for robot mind, physical act, and their coordination in manipulation.</p></div>'
        '<div><h2>Explore</h2><ul>'
        f'<li><a href="{prefix}leaderboard.html">Leaderboard</a></li>'
        f'<li><a href="{prefix}benchmark.html">Benchmark tasks</a></li>'
        f'<li><a href="{prefix}resources.html">Docs</a></li>'
        f'<li><a href="{prefix}protocol.html">Evaluation protocol</a></li>'
        f'<li><a href="{prefix}news.html">News</a></li>'
        f'<li><a href="{prefix}leaderboard.html#submit">Submit a model</a></li>'
        '</ul></div>'
        '<div><h2>Project</h2><ul>'
        '<li><a href="https://mmlab-sigs.github.io/groups/zwang/" target="_blank" rel="noopener">mmlab@SIGS</a></li>'
        '<li><a href="https://www.sigs.tsinghua.edu.cn/" target="_blank" rel="noopener">Tsinghua Shenzhen International Graduate School</a></li>'
        f'<li><a href="{REPO}" target="_blank" rel="noopener">GitHub repository</a></li>'
        f'<li><a href="{prefix}index.html#cite">Cite Mind2Act World</a></li>'
        '</ul></div></div>'
        '<div class="footer-bottom"><span>© 2026 mmlab@SIGS · Mind2Act World</span><span>Simulation demonstrations; scores are reported on the leaderboard.</span></div>'
        '</div></footer>'
    )


_HEADER_RE = re.compile(r'(?:<a class="[a-z-]*skip[a-z-]*" href="#[^"]*">[^<]*</a>)?<header class="header".*?</header>', re.S)
_FOOTER_RE = re.compile(r'<footer class="(?:footer|workspace-footer|docs-footer|site-footer)[^"]*".*?</footer>', re.S)


def apply_shell(page, current='', prefix='', body_class='ds'):
    """Insert tokens/components CSS, replace the legacy header and footer."""
    if 'media/tokens.css' not in page:
        # Shared styles go before the page's own stylesheets so pages can refine them.
        first = re.search(r'<link[^>]+rel="stylesheet"|<style', page)
        head_end = page.find('</head>')
        at = first.start() if first and first.start() < head_end else head_end
        page = page[:at] + head_links(prefix) + page[at:]
    found = re.search(r'<main[^>]*\bid="([^"]+)"', page)
    main_id = found.group(1) if found else 'main'
    if '<header class="site-header"' not in page:
        page, n = _HEADER_RE.subn(lambda _m: header(current, prefix, main_id), page, count=1)
        if not n:
            page = re.sub(r'(<body[^>]*>)', lambda m: m.group(1) + header(current, prefix, main_id), page, count=1)
    if '<footer class="site-footer"' not in page:
        page, n = _FOOTER_RE.subn(lambda _m: footer(prefix), page, count=1)
        if not n:
            page = page.replace('</body>', footer(prefix) + '</body>', 1)
    if body_class:
        def add_class(m):
            tag = m.group(0)
            if 'class="' in tag:
                return tag if re.search(r'class="[^"]*\b' + body_class + r'\b', tag) else tag.replace('class="', f'class="{body_class} ', 1)
            return tag[:-1] + f' class="{body_class}">'
        page = re.sub(r'<body[^>]*>', add_class, page, count=1)
    return page
