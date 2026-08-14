# Emergent Mind Panoramas — in VR

A tiny WebXR viewer that lets you browse the public
[Emergent Mind panoramas](https://www.emergentmind.com/panoramas/) inside a
Meta Quest headset, in fully immersive VR. Point a controller at a thumbnail,
pull the trigger, and you're standing inside the 360° image.

It does **not** proxy or scrape their site at runtime. The panoramas are just
public 4K WebP images served with `Access-Control-Allow-Origin: *`, so the
browser textures them straight onto a sphere. `build.py` collects the current
gallery list once, at build time, into `panoramas.js`.

## What's here

| File | Purpose |
|------|---------|
| `index.html` | The A-Frame WebXR app (gallery + immersive viewer). |
| `panoramas.js` | Generated `window.GALLERY = { loose, collections }` — do not edit by hand. |
| `build.py` | Scrapes the gallery + collections into `panoramas.js`. Re-run to refresh. |
| `vendor/aframe-1.7.1.min.js` | A-Frame, vendored locally (no runtime CDN). |
| `run.sh` | Serves the folder and opens a Cloudflare tunnel over HTTPS. |

## Run it on the Quest

WebXR only turns on over HTTPS, and the Quest can't reach your Mac's
`localhost` — so the page is served locally and exposed through a free
Cloudflare "quick" tunnel (no signup, no account).

```bash
brew install cloudflared      # one-time
./run.sh
```

`run.sh` prints a `https://<random-words>.trycloudflare.com` URL. Open that in
the **Quest browser**, tap **Start**, then press the **goggles / Enter VR**
icon (bottom-right). The URL changes every run; the tunnel lives only while
`run.sh` is running (Ctrl-C stops everything).

Tip: append `?nointro=1` to skip the splash, and `#p=3` to open straight into
panorama #3 (e.g. `https://….trycloudflare.com/?nointro=1#p=3`).

## Controls

The top level shows the three **collections** (World History, Space, Artistic
Styles) as folders, front-and-centre, plus the ~60 loose panoramas. Open a
collection to page through its panoramas (~48 per page).

**In VR:** point a controller at a folder or thumbnail and pull the **trigger**.
**X / Y** = next/prev panorama, or page through a collection. **A / B** = back
(out of a panorama, then out of a collection). **Left grip** = exit VR. Each
controller shows a small **button tooltip**; the gallery re-orients to face you
when you return to it, and **hold the right grip** for a full controls legend.

**On a computer** (for testing): click to open, drag to look around.
<kbd>M</kbd> = back, <kbd>←</kbd> / <kbd>→</kbd> = prev/next or page,
<kbd>H</kbd> = toggle the controls legend. Deep-links: `#c=<slug>` opens a
collection, `#p=<n>` opens loose panorama _n_.

## Refreshing the list

The public gallery shows ~60 loose panoramas plus 3 collections (~554 more).
The list is **static** — baked in at build time, not fetched live. To refresh:

```bash
python3 build.py    # then commit + push; Pages redeploys
```

To always include a specific panorama (even if it's not on the front page), add
its id to the `PINNED` list near the top of `build.py` — it's pinned to the
front of the loose set.

## Permanent hosting (optional)

Everything here is static, so it also drops onto any HTTPS static host
(e.g. GitHub Pages) if you want a permanent bookmark instead of a tunnel.
