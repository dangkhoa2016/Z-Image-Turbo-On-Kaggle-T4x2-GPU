#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="/kaggle/working/Z-Image-Turbo-Kaggle-T4x2-REST-Server"
RUNTIME="$ROOT/.runtime"
for name in tunnel coordinator worker; do
  pidfile="$RUNTIME/$name.pid"
  if [[ -s "$pidfile" ]]; then
    pid="$(cat "$pidfile")"
    if kill -0 "$pid" 2>/dev/null; then kill -TERM "$pid" || true; fi
    rm -f "$pidfile"
  fi
done
printf 'ZIMAGE_SERVER_STOP_REQUESTED=PASS\n'
