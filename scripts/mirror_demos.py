"""Mirror the two Netlify demo sites into the Always Booked repo under /demos/.

Usage: python mirror_demos.py <repo_root>
Downloads index.html, every relative src/href asset, and url(...) assets inside
local CSS files. Injects a noindex meta + a small "Demo built by Always Booked"
bar so the copy doesn't compete with the client's own site in Google.
"""
import os
import re
import sys
import urllib.parse
import urllib.request

SITES = {
    "double-b-barber-studio": "https://majestic-manatee-1ee8d3.netlify.app/",
    "glamour-bridal-salon": "https://ubiquitous-sunburst-8851d3.netlify.app/",
}
UA = {"User-Agent": "Mozilla/5.0"}
ICONS = '<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png"><link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon-16.png"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest"><meta name="theme-color" content="#050a18">'
BAR = '<div id="ab-demo-bar" style="position:fixed;top:0;left:0;right:0;height:34px;line-height:34px;background:#050a18;color:#9db1c4;text-align:center;font:12.5px/34px Inter,system-ui,sans-serif;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding:0 10px;z-index:2147483000;border-bottom:1px solid rgba(0,212,255,.25)">Live demo built by <a href="https://alwaysbookedai.tech/" style="color:#00d4ff;text-decoration:none;font-weight:600">Always Booked</a> &middot; <a href="https://alwaysbookedai.tech/#pricing" style="color:#00d4ff;text-decoration:none">Get a site like this &rarr;</a></div><style>body{padding-top:34px!important}</style><script>(function(){var H=34;function fix(){document.querySelectorAll("body *").forEach(function(el){if(el.id==="ab-demo-bar"||el.closest("#ab-demo-bar"))return;var cs=getComputedStyle(el);if((cs.position==="fixed"||cs.position==="sticky")&&parseFloat(cs.top)===0&&el.getBoundingClientRect().height<200){el.style.top=H+"px";}});}if(document.readyState!=="loading")fix();else document.addEventListener("DOMContentLoaded",fix);})();</script>'


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def is_local(ref):
    if not ref or ref.startswith(("#", "mailto:", "tel:", "data:", "javascript:", "//")):
        return False
    return not urllib.parse.urlparse(ref).scheme


def save(dest_root, rel, data):
    path = os.path.join(dest_root, *rel.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return path


def mirror(slug, base, repo):
    dest = os.path.join(repo, "demos", slug)
    html = fetch(base).decode("utf-8", errors="replace")
    refs = set(re.findall(r'(?:src|href)="([^"]+)"', html))
    css_files = []
    got, failed = [], []
    for ref in sorted(r for r in refs if is_local(r)):
        rel = urllib.parse.urlparse(ref).path.lstrip("./").lstrip("/")
        if not rel or rel.endswith("/"):
            continue
        try:
            data = fetch(urllib.parse.urljoin(base, rel))
            save(dest, rel, data)
            got.append(rel)
            if rel.endswith(".css"):
                css_files.append((rel, data.decode("utf-8", errors="replace")))
        except Exception as e:  # noqa: BLE001 - report and continue
            failed.append(f"{rel}: {e}")
    for css_rel, css in css_files:
        css_dir = os.path.dirname(css_rel)
        for u in re.findall(r'url\(["\']?([^"\')]+)["\']?\)', css):
            if not is_local(u):
                continue
            rel = os.path.normpath(os.path.join(css_dir, u)).replace("\\", "/")
            if rel in got:
                continue
            try:
                save(dest, rel, fetch(urllib.parse.urljoin(base, rel)))
                got.append(rel)
            except Exception as e:  # noqa: BLE001
                failed.append(f"{rel}: {e}")
    html = html.replace("<head>", '<head>\n<meta name="robots" content="noindex, follow">' + ICONS, 1)
    html = re.sub(r"(<body[^>]*>)", r"\1" + BAR, html, count=1)
    save(dest, "index.html", html.encode("utf-8"))
    print(f"[{slug}] assets saved: {len(got)} -> {got}")
    if failed:
        print(f"[{slug}] FAILED: {failed}")


if __name__ == "__main__":
    repo_root = sys.argv[1]
    for s, u in SITES.items():
        mirror(s, u, repo_root)
