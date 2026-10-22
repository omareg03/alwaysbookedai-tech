"""Fetch commercially-licensed blog photos from Openverse (CC0 / PDM / CC BY).

Usage: python fetch_blog_images.py <repo_root> [only_name ...]
Reads IMAGE_SPECS below, saves 1200x675 WebP files to assets/blog/, and merges
credits into assets/blog/credits.json (needed for CC BY attribution).
Pass file names (e.g. roofing-hero) to re-fetch only those, skipping used IDs.
"""
import io
import json
import os
import sys
import time
import urllib.parse
import urllib.request

from PIL import Image

API = "https://api.openverse.org/v1/images/"
UA = {"User-Agent": "AlwaysBookedBlog/1.0 (info@alwaysbookedai.tech)"}
W, H = 1200, 675

IMAGE_SPECS = {
    "missed-call-hero": "barber",
    "missed-call-1": "barber cutting hair",
    "missed-call-2": "smartphone in hand",
    "booksy-hero": "hair salon interior",
    "booksy-1": "hair stylist salon",
    "booksy-2": "calendar",
    "text-back-hero": "man on phone",
    "text-back-1": "text message smartphone",
    "text-back-2": "construction worker",
    "gbp-hero": "shop front",
    "gbp-1": "map on smartphone",
    "gbp-2": "shop owner",
    "reviews-hero": "happy customer shop",
    "reviews-1": "coffee shop counter",
    "reviews-2": "small business owner",
    "no-shows-hero": "appointment calendar",
    "no-shows-1": "empty chairs",
    "no-shows-2": "woman looking at phone",
    "roofing-hero": "roofer working on roof",
    "roofing-1": "roof shingles",
    "roofing-2": "storm clouds",
    "solar-hero": "solar panels on roof",
    "solar-1": "solar panel installation",
    "solar-2": "house with solar panels",
    "med-spa-hero": "spa treatment room",
    "med-spa-1": "facial skincare treatment",
    "med-spa-2": "facial treatment",
    "hvac-hero": "air conditioning technician",
    "hvac-1": "air conditioner",
    "hvac-2": "house at night",
    "dental-hero": "dental office",
    "dental-1": "dental hygienist",
    "dental-2": "dentist office",
    "local-seo-hero": "small town main street",
    "local-seo-1": "laptop analytics",
    "local-seo-2": "city street small businesses",
}


def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def get_bytes(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read()


def to_webp(data, path):
    im = Image.open(io.BytesIO(data)).convert("RGB")
    sw, sh = im.size
    target = W / H
    if sw / sh > target:  # too wide: crop sides
        nw = int(sh * target)
        im = im.crop(((sw - nw) // 2, 0, (sw - nw) // 2 + nw, sh))
    else:  # too tall: crop top/bottom (bias to upper third)
        nh = int(sw / target)
        top = max(0, (sh - nh) // 3)
        im = im.crop((0, top, sw, top + nh))
    im = im.resize((W, H), Image.Resampling.LANCZOS)
    im.save(path, "WEBP", quality=72, method=6)


def main(repo, only):
    out = os.path.join(repo, "assets", "blog")
    os.makedirs(out, exist_ok=True)
    cpath = os.path.join(out, "credits.json")
    credits = json.load(open(cpath, encoding="utf-8")) if os.path.exists(cpath) else {}
    used = {c.get("id") for c in credits.values()}
    for name, query in IMAGE_SPECS.items():
        if only and name not in only:
            continue
        if not only and name in credits and os.path.exists(os.path.join(out, f"{name}.webp")):
            continue  # already fetched on a previous run
        params = urllib.parse.urlencode({
            "q": query, "license": "cc0,pdm,by", "license_type": "commercial",
            "aspect_ratio": "wide", "size": "large", "mature": "false", "page_size": 20,
        })
        try:
            results = get_json(f"{API}?{params}").get("results", [])
        except Exception as e:  # noqa: BLE001
            print(f"{name}: search failed {e}")
            continue
        saved = False
        for r in results:
            if r["id"] in used or (r.get("width") or 0) < 1000:
                continue
            try:
                to_webp(get_bytes(r["url"]), os.path.join(out, f"{name}.webp"))
            except Exception:  # noqa: BLE001 - try the next candidate
                continue
            used.add(r["id"])
            credits[name] = {
                "id": r["id"], "title": r.get("title") or "Untitled",
                "creator": r.get("creator") or "Unknown", "creator_url": r.get("creator_url"),
                "license": r["license"], "license_version": r.get("license_version"),
                "license_url": r.get("license_url"), "landing": r.get("foreign_landing_url"),
                "query": query,
            }
            print(f"{name}: OK [{r['license']}] {credits[name]['title'][:50]} / {credits[name]['creator']}", flush=True)
            json.dump(credits, open(cpath, "w", encoding="utf-8"), indent=1)
            saved = True
            break
        if not saved:
            print(f"{name}: NO RESULT for '{query}'")
        time.sleep(1.2)
    json.dump(credits, open(cpath, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], set(sys.argv[2:]))
