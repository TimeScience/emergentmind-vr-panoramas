#!/usr/bin/env bash
# Serve the VR panorama gallery locally and expose it over HTTPS via a
# Cloudflare quick tunnel (no account/login needed). Open the printed
# https://<random>.trycloudflare.com URL in the Meta Quest browser.
#
#   ./run.sh          # refresh the panorama list, serve, and tunnel
#
# Press Ctrl-C to stop (both the tunnel and the local server shut down).
set -euo pipefail
cd "$(dirname "$0")"

PORT="${PORT:-8137}"

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "cloudflared not found. Install it once with:  brew install cloudflared" >&2
  exit 1
fi

# Refresh the gallery list (non-fatal if offline — keeps the existing file).
python3 build.py || echo "(offline? keeping existing panoramas.js)"

echo "Serving on http://127.0.0.1:${PORT}"
python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT

# Give the server a moment, then open the tunnel (prints the public URL).
until curl -sf -o /dev/null "http://127.0.0.1:${PORT}/panoramas.js"; do sleep 0.3; done
echo
echo "Opening a Cloudflare tunnel — look for the https://<...>.trycloudflare.com URL below,"
echo "then open it (optionally add ?nointro=1) in your Quest browser."
echo
exec cloudflared tunnel --url "http://127.0.0.1:${PORT}"
