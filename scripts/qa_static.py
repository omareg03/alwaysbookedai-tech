"""Static pre-deploy QA for alwaysbookedai.tech.

Usage: python scripts/qa_static.py   (from the repo root). Exit code 1 on errors.
Checks every .html: <img> alt text, local src/href targets exist, JSON-LD parses,
Amazon links carry tag=purefileconve-20 and never use /dp/, title/description length.
"""
import glob
import json
import os
import re
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG = "tag=purefileconve-20"
errors, warns = [], []


def local_target(page, ref):
    path = urllib.parse.urlparse(ref).path
    if path.startswith("/"):
        full = os.path.join(ROOT, *path.strip("/").split("/"))
    else:
        full = os.path.normpath(os.path.join(os.path.dirname(page), *path.split("/")))
    if path.endswith("/") or os.path.isdir(full):
        full = os.path.join(full, "index.html")
    return full


pages = sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True))
amazon_links = 0
for page in pages:
    rel = os.path.relpath(page, ROOT).replace("\\", "/")
    is_demo = rel.startswith("demos/")
    src = open(page, encoding="utf-8", errors="replace").read()
    for tag in re.findall(r"<img\b[^>]*>", src, flags=re.I):
        alt = re.search(r'\balt="([^"]*)"', tag)
        if not alt or not alt.group(1).strip():
            (warns if is_demo else errors).append(f"{rel}: <img> without alt: {tag[:90]}")
    for ref in re.findall(r'(?:src|href)="([^"]+)"', src):
        if ref.startswith(("http:", "https:", "mailto:", "tel:", "#", "data:", "javascript:", "//")):
            continue
        if not os.path.exists(local_target(page, ref)):
            errors.append(f"{rel}: broken local link {ref}")
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', src, flags=re.S):
        try:
            json.loads(block.replace("<\\/", "</"))
        except ValueError as e:
            errors.append(f"{rel}: invalid JSON-LD ({e})")
    for a in re.findall(r'href="(https://www\.amazon\.com[^"]*)"', src):
        amazon_links += 1
        a = a.replace("&amp;", "&")
        if TAG not in a:
            errors.append(f"{rel}: Amazon link missing tag: {a}")
        if "/dp/" in a:
            errors.append(f"{rel}: Amazon /dp/ link (never guess ASINs): {a}")
    if not is_demo:
        t = re.search(r"<title>(.*?)</title>", src, flags=re.S)
        d = re.search(r'<meta name="description" content="([^"]*)"', src)
        if not t:
            errors.append(f"{rel}: missing <title>")
        elif len(t.group(1)) > 75:
            warns.append(f"{rel}: long title ({len(t.group(1))} chars)")
        if not d:
            errors.append(f"{rel}: missing meta description")
        elif not 70 <= len(d.group(1)) <= 170:
            warns.append(f"{rel}: description length {len(d.group(1))}")

print(f"Pages checked: {len(pages)} | Amazon links: {amazon_links}")
for w in warns:
    print("WARN ", w)
for e in errors:
    print("ERROR", e)
print("RESULT:", "FAIL" if errors else "PASS")
sys.exit(1 if errors else 0)
