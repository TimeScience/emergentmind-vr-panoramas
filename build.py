#!/usr/bin/env python3
"""Scrape the public Emergent Mind panorama gallery into panoramas.js.

The main gallery page lists ~60 loose panoramas plus a few collection covers.
Each collection (e.g. /panoramas/world-history) is its own page listing many
panoramas. Full-resolution image URL = thumbnail URL with "_thumb" removed; the
image host sends `Access-Control-Allow-Origin: *`, so the browser can texture
them straight onto a sphere with no proxy.

Emits `window.GALLERY = { loose: [...], collections: [ {slug,title,cover,items} ] }`.

Re-run any time to refresh the list:  python3 build.py
"""
import html
import json
import re
import sys
import urllib.request

INDEX_URL = "https://www.emergentmind.com/panoramas/"
PANO_URL = "https://www.emergentmind.com/panoramas/{slug}"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
OUT = "panoramas.js"

# Individual panorama ids to always pin to the front of the loose set, even if
# they're not on the current front page.
PINNED = ["4243675f"]  # "Psychedelic Bubble Sphere"

# Each gallery item is an <a href="/panoramas/..."> wrapping a thumbnail <img>.
# Individual panoramas have an opaque hex id; collections have a word slug.
ANCHOR = re.compile(r'<a\b[^>]*href="/panoramas/([^"]+)"[^>]*>(.*?)</a>', re.I | re.S)
IMG_TAG = re.compile(r"<img\b[^>]*panorama_\d+_thumb_[a-f0-9]+\.webp[^>]*>", re.I)
SRC = re.compile(r'src="([^"]+)"')
ALT = re.compile(r'alt="([^"]*)"')
HEX_ID = re.compile(r"[a-f0-9]{6,}$")
# On an individual panorama page: the full-res image and the title.
PANO_IMG = re.compile(r'data-panorama-image-value="([^"]+)"')
OG_TITLE = re.compile(r'og:title" content="([^"]*)"')
FULL_TO_THUMB = re.compile(r"(panorama_\d+)_([a-f0-9]+\.webp)")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace")


def titleize_slug(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ").title()


def pano_from_anchor(block: str):
    """Return {full, thumb, title} for a gallery anchor block, or None."""
    tag = IMG_TAG.search(block)
    if not tag:
        return None
    m = SRC.search(tag.group(0))
    if not m:
        return None
    thumb = m.group(1)
    alt = ALT.search(tag.group(0))
    title = html.unescape(alt.group(1)).strip() if alt else ""
    return {"full": thumb.replace("_thumb", ""), "thumb": thumb, "title": title}


def fetch_pinned(pid: str):
    """Fetch an individual panorama page → {full, thumb, title}, or None."""
    page = fetch(PANO_URL.format(slug=pid))
    m = PANO_IMG.search(page)
    if not m:
        return None
    full = m.group(1)
    thumb = FULL_TO_THUMB.sub(r"\1_thumb_\2", full)
    t = OG_TITLE.search(page)
    title = html.unescape(t.group(1)).strip() if t else "Untitled"
    return {"full": full, "thumb": thumb, "title": title or "Untitled"}


def parse_panoramas(page: str, hex_only: bool):
    """All panoramas on a page, deduped by full URL, in document order."""
    seen, out = set(), []
    for slug, block in ANCHOR.findall(page):
        if hex_only and not HEX_ID.fullmatch(slug):
            continue
        p = pano_from_anchor(block)
        if not p or p["full"] in seen:
            continue
        seen.add(p["full"])
        if not p["title"]:
            p["title"] = "Untitled" if hex_only else titleize_slug(slug)
        out.append(p)
    return out


def main() -> int:
    index = fetch(INDEX_URL)

    loose, collections, seen_cov = [], [], set()
    seen_loose = set()
    for slug, block in ANCHOR.findall(index):
        p = pano_from_anchor(block)
        if not p:
            continue
        if HEX_ID.fullmatch(slug):
            if p["full"] in seen_loose:
                continue
            seen_loose.add(p["full"])
            if not p["title"]:
                p["title"] = "Untitled"
            loose.append(p)
        else:  # a collection cover
            if slug in seen_cov:
                continue
            seen_cov.add(slug)
            collections.append({"slug": slug, "cover": {"full": p["full"], "thumb": p["thumb"]}})

    # Pin explicit panoramas to the front of the loose set (deduped).
    for pid in reversed(PINNED):
        p = fetch_pinned(pid)
        if p and p["full"] not in seen_loose:
            seen_loose.add(p["full"])
            loose.insert(0, p)
            print(f"  pinned {pid}: {p['title']}")
        elif not p:
            print(f"  WARNING: could not fetch pinned {pid}", file=sys.stderr)

    for c in collections:
        items = parse_panoramas(fetch(PANO_URL.format(slug=c["slug"])), hex_only=True)
        c["title"] = titleize_slug(c["slug"])
        c["items"] = items
        print(f"  collection {c['slug']}: {len(items)} panoramas")

    if not loose and not collections:
        print("ERROR: nothing parsed — site markup may have changed.", file=sys.stderr)
        return 1

    gallery = {"loose": loose, "collections": collections}
    total = len(loose) + sum(len(c["items"]) for c in collections)
    js = (
        "// Auto-generated by build.py — do not edit by hand.\n"
        f"// Source: {INDEX_URL}\n"
        f"// {len(loose)} loose panoramas, {len(collections)} collections, {total} total.\n"
        "window.GALLERY = " + json.dumps(gallery, ensure_ascii=False, indent=1) + ";\n"
    )
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(js)
    print(f"Wrote {OUT}: {len(loose)} loose + {len(collections)} collections ({total} total).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
