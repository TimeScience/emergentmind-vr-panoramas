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
| `panoramas.js` | Generated list of `{full, thumb, title}` — do not edit by hand. |
| `build.py` | Scrapes the gallery into `panoramas.js`. Re-run to refresh. |
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

**In VR:** point a controller at a thumbnail and pull the **trigger** to open
it. Then: **X** = next, **Y** = prev, **A/B** = back to gallery, **left grip**
= exit VR. The controls are hidden to keep the view clean — **hold the right
grip** to peek at them.

**On a computer** (for testing): click a thumbnail, drag to look around.
<kbd>M</kbd> = back to gallery, <kbd>←</kbd> / <kbd>→</kbd> = prev / next,
<kbd>H</kbd> = toggle the controls legend.

## Refreshing the list

The public gallery shows ~63 curated panoramas. To pick up new ones later:

```bash
python3 build.py
```

## Permanent hosting (optional)

Everything here is static, so it also drops onto any HTTPS static host
(e.g. GitHub Pages) if you want a permanent bookmark instead of a tunnel.
