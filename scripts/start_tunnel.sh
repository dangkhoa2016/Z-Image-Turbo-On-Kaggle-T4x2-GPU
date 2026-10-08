#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="/kaggle/working/Z-Image-Turbo-Kaggle-T4x2-REST-Server"
RUNTIME="$ROOT/.runtime"
BIN="$RUNTIME/cloudflared"
LOG="$ROOT/logs/tunnel.log"
mkdir -p "$RUNTIME" "$ROOT/logs"

python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8090/health',timeout=3)" >/dev/null
if [[ ! -x "$BIN" ]]; then
  curl -fL --retry 3 -o "$BIN" https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
  chmod 755 "$BIN"
fi

if [[ -s "$RUNTIME/tunnel.pid" ]] && kill -0 "$(cat "$RUNTIME/tunnel.pid")" 2>/dev/null; then
  :
else
  : > "$LOG"
  nohup "$BIN" tunnel --no-autoupdate --url http://127.0.0.1:8090 >"$LOG" 2>&1 &
  echo $! > "$RUNTIME/tunnel.pid"
fi

for _ in $(seq 1 30); do
  url="$(grep -Eo 'https://[-a-z0-9]+\.trycloudflare\.com' "$LOG" | tail -1 || true)"
  if [[ -n "$url" ]]; then
    printf '%s' "$url" > "$RUNTIME/tunnel_url"
    printf 'TUNNEL_READY=PASS\nPUBLIC_URL=%s\n' "$url"
    exit 0
  fi
  sleep 1
done
cat "$LOG"
exit 1
