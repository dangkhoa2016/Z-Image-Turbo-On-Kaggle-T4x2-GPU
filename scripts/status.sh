#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="/kaggle/working/Z-Image-Turbo-Kaggle-T4x2-REST-Server"
python3 "$ROOT/scripts/local_control_acceptance.py"
if [[ -s "$ROOT/.runtime/tunnel_url" ]]; then printf 'PUBLIC_URL=%s\n' "$(cat "$ROOT/.runtime/tunnel_url")"; fi
