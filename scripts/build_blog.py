"""Render the Always Booked blog: posts, index, sitemap, homepage "latest posts".

Usage: python scripts/build_blog.py   (run from the repo root)
Inputs: scripts/blog_posts.py (content), assets/blog/<img>-{hero,1,2}.webp,
        assets/blog/credits.json (photo licenses).
"""
import html
import json
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blog_posts import DATE, POSTS, SEO_TITLES  # noqa: E402

SITE = "https://alwaysbookedai.tech"
TAG = "purefileconve-20"
BOOKING = "https://api.leadconnectorhq.com/widget/bookings/discovery-call-omar"
FIVERR = "https://www.fiverr.com/omareg03"
PFC = "https://purefileconverter.com"
MFNF = "https://www.youtube.com/@MyFrenchiesNFriends"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDITS = json.load(open(os.path.join(ROOT, "assets", "blog", "credits.json"), encoding="utf-8"))
E = html.escape


def amazon(keywords):
    return f"https://www.amazon.com/s?k={urllib.parse.quote_plus(keywords)}&tag={TAG}"


def ld(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1).replace("</", "<\\/")


def credit(name):
    c = CREDITS.get(name) or {}
    lic = c.get("license")
    creator = c.get("creator") or "Unknown"
    if lic == "ai":
        return "AI-generated image"
    if lic == "unsplash":
        return 'Photo: <a href="https://unsplash.com/license" rel="noopener" target="_blank">Unsplash</a>'
    if lic == "by":
        ver = c.get("license_version") or ""
        return (f'Photo: <a href="{E(c.get("landing") or "#")}" rel="noopener nofollow" target="_blank">'
                f'{E(c.get("title") or "Untitled")}</a> by {E(creator)}, '
                f'<a href="{E(c.get("license_url") or "#")}" rel="noopener nofollow" target="_blank">CC BY {E(ver)}</a>')
    who = "" if creator == "Unknown" else f" by {E(creator)}"
    label = "Public domain" if lic == "pdm" else "CC0"
    return f'Photo{who} via <a href="{E(c.get("landing") or "#")}" rel="noopener nofollow" target="_blank">Openverse</a> ({label})'


def figure(post, n):
    name = f'{post["img"]}-{n}'
    return (f'<figure class="fig"><img src="/assets/blog/{name}.webp" width="1200" height="675" loading="lazy" '
            f'decoding="async" alt="{E(post["alts"][str(n)])}"><figcaption>{credit(name)}</figcaption></figure>')


BASE_CSS = """
:root{--navy:#050a18;--navy2:#0b1630;--accent:#00d4ff;--deep:#0077b6;--warm:#ffb020;--ink:#14213d;--body:#3d4b63;--paper:#f5f8fc;--card:#fff;--line:#e3e9f2}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{font-family:'Inter',system-ui,-apple-system,sans-serif;background:var(--paper);color:var(--body);line-height:1.75;-webkit-font-smoothing:antialiased}
a{color:var(--deep)}
img{max-width:100%;display:block}
h1,h2,h3{font-family:'Space Grotesk','Inter',sans-serif;color:var(--ink);line-height:1.25}
.topbar{position:sticky;top:0;z-index:50;background:rgba(5,10,24,.92);backdrop-filter:blur(10px);border-bottom:1px solid rgba(0,212,255,.12)}
.topbar .in{max-width:1180px;margin:0 auto;padding:.85rem 5%;display:flex;align-items:center;justify-content:space-between;gap:1rem}
.brand{display:flex;align-items:center;gap:.55rem;color:#fff;font-weight:800;text-decoration:none;font-family:'Space Grotesk',sans-serif}
.brand img{width:34px;height:auto}
.nav{display:flex;align-items:center;gap:1.4rem}
.nav a{color:#b8c7d9;text-decoration:none;font-weight:600;font-size:.92rem}
.nav a:hover,.nav a.on{color:var(--accent)}
.btn{display:inline-flex;align-items:center;gap:.4rem;font-weight:800;text-decoration:none;border-radius:10px;padding:.7rem 1.25rem;transition:transform .2s,box-shadow .2s}
.btn:hover{transform:translateY(-2px)}
.btn-warm{background:var(--warm);color:#1c1300;box-shadow:0 8px 24px rgba(255,176,32,.28)}
.btn-ghost{border:1.5px solid rgba(0,212,255,.55);color:#e9f8ff}
.btn-sm{padding:.5rem .95rem;font-size:.85rem}
@media(max-width:760px){.nav a:not(.btn){display:none}}
footer.site{background:var(--navy);color:#8ea2b8;padding:3rem 5% 2.2rem;margin-top:4rem}
footer.site .in{max-width:1180px;margin:0 auto;display:grid;grid-template-columns:2fr 1fr 1fr;gap:2rem}
footer.site h4{color:#fff;font-family:'Space Grotesk',sans-serif;margin-bottom:.7rem;font-size:.95rem}
footer.site a{color:#b8c7d9;text-decoration:none;display:block;margin:.3rem 0;font-size:.9rem}
footer.site a:hover{color:var(--accent)}
footer.site .fine{max-width:1180px;margin:2rem auto 0;border-top:1px solid rgba(255,255,255,.07);padding-top:1.2rem;font-size:.78rem;color:#6e8299}
@media(max-width:760px){footer.site .in{grid-template-columns:1fr}}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet">')


def topbar(active="blog"):
    on = ' class="on"' if active == "blog" else ""
    return f"""<header class="topbar"><div class="in">
<a class="brand" href="/"><img src="/assets/logo.png" width="34" height="24" alt="Always Booked logo">Always Booked</a>
<nav class="nav"><a href="/#solutions">Solutions</a><a href="/#portfolio">Portfolio</a><a href="/#pricing">Pricing</a><a href="/blog/"{on}>Blog</a>
<a class="btn btn-warm btn-sm" href="{BOOKING}" target="_blank" rel="noopener">Book a free call</a></nav></div></header>"""


def footer():
    return f"""<footer class="site"><div class="in">
<div><a class="brand" href="/"><img src="/assets/logo.png" width="34" height="24" alt="Always Booked logo">Always Booked</a>
<p style="margin-top:.8rem;font-size:.9rem;max-width:420px">AI front-desk, online booking, missed-call text-back and Google review automation for local service businesses. Orlando, FL &middot; info@alwaysbookedai.tech</p></div>
<div><h4>Explore</h4><a href="/">Home</a><a href="/#pricing">Plans &amp; pricing</a><a href="/blog/">Blog</a><a href="{BOOKING}" target="_blank" rel="noopener">Book a discovery call</a></div>
<div><h4>More from us</h4><a href="{PFC}" target="_blank" rel="noopener">Free file tools (PureFileConverter)</a><a href="{FIVERR}" target="_blank" rel="noopener">Services on Fiverr</a><a href="{MFNF}" target="_blank" rel="noopener">My Frenchies N' Friends</a></div>
</div><p class="fine">&copy; 2026 Always Booked. As an Amazon Associate I earn from qualifying purchases. Some links on this site are affiliate links.</p></footer>"""


POST_CSS = """
.progress{position:fixed;top:0;left:0;height:3px;width:0;background:linear-gradient(90deg,var(--accent),var(--warm));z-index:60}
.hero{position:relative;min-height:clamp(340px,56vh,540px);display:flex;align-items:flex-end;color:#fff;overflow:hidden;background:var(--navy)}
.hero>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.hero:after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(5,10,24,.15) 0%,rgba(5,10,24,.55) 45%,rgba(5,10,24,.95) 100%)}
.hero .in{position:relative;z-index:2;max-width:860px;margin:0 auto;padding:3rem 5% 2.6rem;width:100%}
.crumbs{font-size:.82rem;color:#b8c7d9;margin-bottom:.9rem}
.crumbs a{color:#b8c7d9;text-decoration:none}.crumbs a:hover{color:var(--accent)}
.chip{display:inline-block;background:rgba(0,212,255,.16);border:1px solid rgba(0,212,255,.45);color:#bff3ff;font-size:.74rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:.28rem .7rem;border-radius:99px;margin-bottom:.9rem;text-decoration:none}
.hero h1{color:#fff;font-size:clamp(1.8rem,4.6vw,2.9rem);margin-bottom:.8rem;text-shadow:0 2px 18px rgba(0,0,0,.35)}
.hero .lede{color:#d6e2ef;max-width:680px;font-size:1.05rem}
.meta{display:flex;align-items:center;gap:.7rem;margin-top:1.2rem;font-size:.86rem;color:#c3d1e0}
.meta img{width:38px;height:38px;border-radius:50%;object-fit:cover;border:2px solid var(--accent)}
.wrap{max-width:780px;margin:0 auto;padding:2.4rem 5% 0}
.disclose{font-size:.8rem;color:#6b7a90;background:#fff;border:1px solid var(--line);border-radius:10px;padding:.7rem 1rem;margin-bottom:2rem}
article h2{font-size:1.55rem;margin:2.4rem 0 .8rem}
article h3{font-size:1.15rem;margin:1.6rem 0 .5rem}
article p,article li{font-size:1.06rem;margin-bottom:1rem}
article ul,article ol{padding-left:1.35rem;margin-bottom:1.2rem}
article li::marker{color:var(--deep);font-weight:700}
article strong{color:var(--ink)}
article em{color:#2c3d57}
article .note{font-size:.88rem;color:#6b7a90;border-left:3px solid var(--accent);padding:.4rem .9rem;background:#fff;border-radius:0 8px 8px 0}
article table{width:100%;border-collapse:collapse;margin:1.4rem 0;font-size:.95rem;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(20,33,61,.06)}
article th,article td{padding:.75rem .9rem;border-bottom:1px solid var(--line);text-align:left}
article th{background:var(--navy2);color:#fff;font-family:'Space Grotesk',sans-serif}
.fig{margin:2rem 0}
.fig img{width:100%;height:auto;border-radius:16px;box-shadow:0 14px 40px rgba(20,33,61,.16)}
.fig figcaption{font-size:.76rem;color:#7d8ba0;margin-top:.55rem;text-align:center}
.fig figcaption a{color:#7d8ba0}
.tools{margin:3rem 0 0;background:#fff;border:1px solid var(--line);border-radius:18px;padding:1.8rem;box-shadow:0 8px 30px rgba(20,33,61,.06)}
.tools h2{margin:0 0 .3rem;font-size:1.35rem}
.tools .small{font-size:.8rem;color:#6b7a90;margin-bottom:1.2rem}
.tgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem}
.tool{border:1px solid var(--line);border-radius:14px;padding:1.1rem;display:flex;flex-direction:column;gap:.5rem;transition:border-color .2s,transform .2s}
.tool:hover{border-color:var(--accent);transform:translateY(-3px)}
.tool b{color:var(--ink);font-family:'Space Grotesk',sans-serif}
.tool span{font-size:.9rem;flex:1}
.tool a{align-self:flex-start;background:#ff9900;color:#111;font-weight:800;font-size:.85rem;padding:.5rem .9rem;border-radius:8px;text-decoration:none}
.tool a:hover{background:#ffad33}
.cta{margin:2.6rem 0 0;border-radius:20px;padding:2.2rem;background:radial-gradient(120% 140% at 0% 0%,#0d2a4f 0%,var(--navy) 60%);color:#d6e2ef;position:relative;overflow:hidden}
.cta:before{content:'';position:absolute;right:-60px;top:-60px;width:220px;height:220px;border-radius:50%;background:radial-gradient(circle,rgba(0,212,255,.35),transparent 70%)}
.cta h2{color:#fff;margin:0 0 .5rem;font-size:1.6rem;position:relative}
.cta p{position:relative;margin-bottom:1.2rem}
.cta .row{display:flex;flex-wrap:wrap;gap:.8rem;position:relative}
.related{max-width:1180px;margin:3.5rem auto 0;padding:0 5%}
.related h2{font-size:1.5rem;margin-bottom:1.2rem}
"""

CARD_CSS = """
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1.5rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:18px;overflow:hidden;text-decoration:none;color:inherit;display:flex;flex-direction:column;transition:transform .25s,box-shadow .25s,border-color .25s}
.card:hover{transform:translateY(-6px);box-shadow:0 18px 44px rgba(20,33,61,.14);border-color:rgba(0,119,182,.35)}
.card .ph{aspect-ratio:16/9;overflow:hidden;background:var(--navy2)}
.card .ph img{width:100%;height:100%;object-fit:cover;transition:transform .6s}
.card:hover .ph img{transform:scale(1.06)}
.card .tx{padding:1.2rem 1.3rem 1.4rem;display:flex;flex-direction:column;gap:.45rem;flex:1}
.card .cat{font-size:.72rem;font-weight:800;letter-spacing:.07em;text-transform:uppercase;color:var(--deep)}
.card h3{font-size:1.12rem}
.card p{font-size:.92rem;color:#5a6a82;flex:1}
.card .more{font-weight:700;color:var(--deep);font-size:.9rem}
"""


def card(p, featured=False):
    cls = "card feat" if featured else "card"
    return (f'<a class="{cls}" href="/blog/{p["slug"]}/" data-cat="{E(p["category"])}">'
            f'<div class="ph"><img src="/assets/blog/{p["img"]}-hero.webp" width="1200" height="675" loading="lazy" decoding="async" alt="{E(p["alts"]["hero"])}"></div>'
            f'<div class="tx"><span class="cat">{E(p["category"])} &middot; {p["read"]} min read</span>'
            f'<h3>{E(p["title"])}</h3><p>{E(p["description"])}</p><span class="more">Read article &rarr;</span></div></a>')


def related_for(p):
    same = [q for q in POSTS if q["slug"] != p["slug"] and q["category"] == p["category"]]
    rest = [q for q in POSTS if q["slug"] != p["slug"] and q not in same]
    return (same + rest)[:3]


def render_post(p):
    url = f"{SITE}/blog/{p['slug']}/"
    hero = f"{SITE}/assets/blog/{p['img']}-hero.webp"
    body = p["body"].replace("{IMG1}", figure(p, 1)).replace("{IMG2}", figure(p, 2))
    tools = "".join(
        f'<div class="tool"><b>{E(n)}</b><span>{E(w)}</span>'
        f'<a href="{E(amazon(k))}" target="_blank" rel="sponsored nofollow noopener">View on Amazon &rarr;</a></div>'
        for n, w, k in p["affiliate"])
    schema = [
        {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"],
         "description": p["description"], "image": [hero, f"{SITE}/assets/blog/{p['img']}-1.webp", f"{SITE}/assets/blog/{p['img']}-2.webp"],
         "datePublished": DATE, "dateModified": DATE, "articleSection": p["category"],
         "author": {"@type": "Person", "name": "Omy Grace", "url": f"{SITE}/#about"},
         "publisher": {"@type": "Organization", "name": "Always Booked", "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/logo.png"}},
         "mainEntityOfPage": {"@type": "WebPage", "@id": url}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"},
            {"@type": "ListItem", "position": 3, "name": p["title"], "item": url}]},
    ]
    rel = "".join(card(q) for q in related_for(p))
    t = E(p["title"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{E(SEO_TITLES.get(p["slug"], p["title"] + " | Always Booked"))}</title>
<meta name="description" content="{E(p['description'])}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Always Booked">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{E(p['description'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{hero}">
<meta property="og:image:alt" content="{E(p['alts']['hero'])}">
<meta property="article:published_time" content="{DATE}">
<meta property="article:section" content="{E(p['category'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{E(p['description'])}">
<meta name="twitter:image" content="{hero}">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
<link rel="preload" as="image" href="/assets/blog/{p['img']}-hero.webp">
{FONTS}
<script type="application/ld+json">{ld(schema)}</script>
<style>{BASE_CSS}{POST_CSS}{CARD_CSS}</style>
</head>
<body>
<div class="progress" id="progress"></div>
{topbar()}
<section class="hero">
<img src="/assets/blog/{p['img']}-hero.webp" width="1200" height="675" fetchpriority="high" alt="{E(p['alts']['hero'])}">
<div class="in">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> &rsaquo; <a href="/blog/">Blog</a> &rsaquo; {E(p['category'])}</nav>
<a class="chip" href="/blog/?cat={urllib.parse.quote(p['category'])}">{E(p['category'])}</a>
<h1>{t}</h1>
<p class="lede">{E(p['description'])}</p>
<div class="meta"><img src="/assets/founder.png" width="38" height="38" alt="Omy Grace, founder of Always Booked"><span><strong style="color:#fff">Omy Grace</strong> &middot; Founder &middot; October 2026 &middot; {p['read']} min read</span></div>
</div>
</section>
<main class="wrap">
<p class="disclose">This article contains affiliate links. As an Amazon Associate I earn from qualifying purchases, at no extra cost to you.</p>
<article>
{body}
<section class="tools" aria-labelledby="tools-h">
<h2 id="tools-h">Tools we recommend</h2>
<p class="small">Hand-picked, inexpensive tools that pair with this guide. Affiliate links; prices on Amazon.</p>
<div class="tgrid">{tools}</div>
</section>
<section class="cta">
<h2>Stop losing the customers you never hear from.</h2>
<p>Always Booked sets up 24/7 AI front-desk, online booking, missed-call text-back and review automation for local businesses.</p>
<div class="row"><a class="btn btn-warm" href="/#pricing">See plans &amp; pricing</a><a class="btn btn-ghost" href="{BOOKING}" target="_blank" rel="noopener">Book a free discovery call</a></div>
</section>
</article>
</main>
<section class="related"><h2>Keep reading</h2><div class="cards">{rel}</div></section>
{footer()}
<script>
(function(){{var b=document.getElementById('progress');function u(){{var h=document.documentElement,s=h.scrollTop||document.body.scrollTop,m=h.scrollHeight-h.clientHeight;b.style.width=(m>0?s/m*100:0)+'%';}}document.addEventListener('scroll',u,{{passive:true}});u();}})();
</script>
</body>
</html>
"""


def render_index():
    cats = []
    for p in POSTS:
        if p["category"] not in cats:
            cats.append(p["category"])
    chips = '<button class="fchip on" data-f="all">All</button>' + "".join(
        f'<button class="fchip" data-f="{E(c)}">{E(c)}</button>' for c in cats)
    feat, rest = POSTS[0], POSTS[1:]
    schema = {"@context": "https://schema.org", "@type": "Blog", "name": "Always Booked Blog", "url": f"{SITE}/blog/",
              "description": "Guides on missed calls, booking, reviews, local SEO and AI front-desk automation for local service businesses.",
              "publisher": {"@type": "Organization", "name": "Always Booked", "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/logo.png"}},
              "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": f"{SITE}/blog/{p['slug']}/",
                            "image": f"{SITE}/assets/blog/{p['img']}-hero.webp", "datePublished": DATE} for p in POSTS]}
    idx_css = """
.bhero{background:radial-gradient(90% 120% at 15% 0%,#0f2f57 0%,var(--navy) 55%);color:#d6e2ef;padding:4.2rem 5% 3.4rem;position:relative;overflow:hidden}
.bhero:after{content:'';position:absolute;right:-120px;top:-120px;width:420px;height:420px;border-radius:50%;background:radial-gradient(circle,rgba(0,212,255,.22),transparent 70%)}
.bhero .in{max-width:1180px;margin:0 auto;position:relative;z-index:1}
.bhero .k{color:var(--accent);font-weight:800;letter-spacing:.12em;text-transform:uppercase;font-size:.78rem}
.bhero h1{color:#fff;font-size:clamp(2rem,5vw,3.2rem);margin:.5rem 0 .8rem}
.bhero p{max-width:640px;font-size:1.08rem}
.filters{display:flex;flex-wrap:wrap;gap:.55rem;margin-top:1.8rem}
.fchip{font:inherit;font-size:.86rem;font-weight:700;cursor:pointer;border-radius:99px;padding:.5rem 1rem;border:1.5px solid rgba(0,212,255,.35);background:rgba(255,255,255,.04);color:#cfe9f5;transition:all .2s}
.fchip:hover{border-color:var(--accent);color:#fff}
.fchip.on{background:var(--accent);border-color:var(--accent);color:#04121f}
.grid-wrap{max-width:1180px;margin:2.6rem auto 0;padding:0 5%}
.card.feat{grid-column:1/-1;flex-direction:row}
.card.feat .ph{flex:1.25;aspect-ratio:auto;min-height:320px}
.card.feat .tx{flex:1;padding:2rem;justify-content:center}
.card.feat h3{font-size:1.65rem}
@media(max-width:860px){.card.feat{flex-direction:column}.card.feat .ph{min-height:0;aspect-ratio:16/9}}
.card.hide{display:none}
"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Blog: Booking, Reviews, Local SEO &amp; AI Front Desk | Always Booked</title>
<meta name="description" content="Practical guides for local service businesses: missed calls, online booking, Google reviews, local SEO and AI front-desk automation. New articles every week.">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{SITE}/blog/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Always Booked">
<meta property="og:title" content="The Always Booked Blog">
<meta property="og:description" content="Guides on missed calls, booking, reviews and local SEO for service businesses.">
<meta property="og:url" content="{SITE}/blog/">
<meta property="og:image" content="{SITE}/assets/blog/{feat['img']}-hero.webp">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
{FONTS}
<script type="application/ld+json">{ld(schema)}</script>
<style>{BASE_CSS}{CARD_CSS}{idx_css}</style>
</head>
<body>
{topbar()}
<section class="bhero"><div class="in">
<span class="k">The Always Booked Blog</span>
<h1>Fill your calendar. Keep every customer.</h1>
<p>Straight-talk guides for owners of salons, clinics, contractors and home-service companies: missed calls, booking, reviews and local SEO. New articles every week.</p>
<div class="filters" role="group" aria-label="Filter articles by category">{chips}</div>
</div></section>
<main class="grid-wrap"><div class="cards" id="cards">{card(feat, True)}{"".join(card(p) for p in rest)}</div></main>
{footer()}
<script>
(function(){{
var chips=document.querySelectorAll('.fchip'),cards=document.querySelectorAll('#cards .card');
function apply(f){{chips.forEach(function(c){{c.classList.toggle('on',c.dataset.f===f);}});
cards.forEach(function(k){{k.classList.toggle('hide',f!=='all'&&k.dataset.cat!==f);}});}}
chips.forEach(function(c){{c.addEventListener('click',function(){{apply(c.dataset.f);history.replaceState(null,'',c.dataset.f==='all'?'/blog/':'/blog/?cat='+encodeURIComponent(c.dataset.f));}});}});
var q=new URLSearchParams(location.search).get('cat');if(q){{apply(q);}}
}})();
</script>
</body>
</html>
"""


def render_home_section():
    picks = POSTS[:3]
    cards = "".join(
        f'<a class="abb-card" href="/blog/{p["slug"]}/"><div class="abb-ph"><img src="/assets/blog/{p["img"]}-hero.webp" '
        f'width="1200" height="675" loading="lazy" decoding="async" alt="{E(p["alts"]["hero"])}"></div>'
        f'<div class="abb-tx"><span>{E(p["category"])}</span><h3>{E(p["title"])}</h3><b>Read article &rarr;</b></div></a>'
        for p in picks)
    return f"""<!-- BLOG-LATEST:START -->
<section class="abb" id="blog">
<style>
.abb{{position:relative;z-index:10;padding:5rem 5%;max-width:1200px;margin:0 auto}}
.abb-head{{text-align:center;margin-bottom:2.4rem}}
.abb-head .k{{color:var(--accent);font-weight:800;letter-spacing:.12em;text-transform:uppercase;font-size:.78rem}}
.abb-head h2{{font-family:'Space Grotesk',sans-serif;color:#fff;font-size:clamp(1.8rem,4vw,2.6rem);margin:.4rem 0}}
.abb-head p{{color:var(--text-muted)}}
.abb-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.5rem}}
.abb-card{{background:var(--panel);border:1px solid var(--panel-border);border-radius:18px;overflow:hidden;text-decoration:none;transition:transform .3s,border-color .3s,box-shadow .3s}}
.abb-card:hover{{transform:translateY(-6px);border-color:var(--accent);box-shadow:0 18px 50px rgba(0,212,255,.15)}}
.abb-ph{{aspect-ratio:16/9;overflow:hidden}}
.abb-ph img{{width:100%;height:100%;object-fit:cover;transition:transform .6s}}
.abb-card:hover .abb-ph img{{transform:scale(1.06)}}
.abb-tx{{padding:1.2rem 1.3rem 1.4rem}}
.abb-tx span{{color:var(--accent);font-size:.72rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase}}
.abb-tx h3{{color:#fff;font-family:'Space Grotesk',sans-serif;font-size:1.08rem;margin:.45rem 0 .7rem;line-height:1.35}}
.abb-tx b{{color:var(--accent);font-size:.88rem}}
.abb-all{{text-align:center;margin-top:2rem}}
.abb-all a{{display:inline-block;border:1.5px solid var(--accent);color:var(--accent);padding:.75rem 1.5rem;border-radius:10px;font-weight:700;text-decoration:none}}
.abb-all a:hover{{background:var(--accent);color:#04121f}}
</style>
<div class="abb-head"><span class="k">From the blog</span><h2>Guides that keep your calendar full</h2><p>Practical playbooks on missed calls, booking, reviews and local SEO.</p></div>
<div class="abb-grid">{cards}</div>
<div class="abb-all"><a href="/blog/">See all {len(POSTS)} articles &rarr;</a></div>
</section>
<!-- BLOG-LATEST:END -->"""


def write(rel, text):
    path = os.path.join(ROOT, *rel.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main():
    missing = [f"{p['img']}-{n}" for p in POSTS for n in ("hero", "1", "2")
               if not os.path.exists(os.path.join(ROOT, "assets", "blog", f"{p['img']}-{n}.webp"))]
    if missing:
        sys.exit(f"Missing images: {missing}")
    for p in POSTS:
        write(f"blog/{p['slug']}/index.html", render_post(p))
    write("blog/index.html", render_index())
    urls = [f"{SITE}/", f"{SITE}/blog/"] + [f"{SITE}/blog/{p['slug']}/" for p in POSTS]
    sm = "\n".join(f"  <url><loc>{u}</loc><lastmod>{DATE}</lastmod></url>" for u in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}\n</urlset>\n')
    home_path = os.path.join(ROOT, "index.html")
    home = open(home_path, encoding="utf-8", newline="").read()
    section = render_home_section()
    if "<!-- BLOG-LATEST:START -->" in home:
        home = re.sub(r"<!-- BLOG-LATEST:START -->.*?<!-- BLOG-LATEST:END -->", lambda m: section, home, flags=re.S)
    else:
        anchor = "<!-- ABOUT THE FOUNDER & FOOTER -->"
        if anchor not in home:
            sys.exit("Homepage anchor not found")
        home = home.replace(anchor, section + "\n\n    " + anchor, 1)
    with open(home_path, "w", encoding="utf-8", newline="") as f:
        f.write(home)
    print(f"Built {len(POSTS)} posts, blog index, sitemap ({len(urls)} URLs), homepage section.")


if __name__ == "__main__":
    main()
