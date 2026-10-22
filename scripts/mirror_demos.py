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
BAR = (
    '<div style="background:#050a18;color:#9db1c4;text-align:center;padding:8px 12px;'
    'font:13px/1.4 Inter,system-ui,sans-serif;position:relative;z-index:99999">'
    'Live demo built by <a href="https://alwaysbookedai.tech/" style="color:#00d4ff;'
    'text-decoration:none;font-weight:600">Always Booked</a> &middot; '
    '<a href="https://alwaysbookedai.tech/#pricing" style="color:#00d4ff;text-decoration:none">'
    'Get a site like this &rarr;</a></div>'
)


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
    html = html.replace("<head>", '<head>\n<meta name="robots" content="noindex">', 1)
    html = re.sub(r"(<body[^>]*>)", r"\1" + BAR, html, count=1)
    save(dest, "index.html", html.encode("utf-8"))
    print(f"[{slug}] assets saved: {len(got)} -> {got}")
    if failed:
        print(f"[{slug}] FAILED: {failed}")


if __name__ == "__main__":
    repo_root = sys.argv[1]
    for s, u in SITES.items():
        mirror(s, u, repo_root)
