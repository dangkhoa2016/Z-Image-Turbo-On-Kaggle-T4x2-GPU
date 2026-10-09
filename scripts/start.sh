#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="/kaggle/working/Z-Image-Turbo-Kaggle-T4x2-REST-Server"
RUNTIME="$ROOT/.runtime"
mkdir -p "$RUNTIME" "$ROOT/logs" "$ROOT/outputs" "$ROOT/metadata" "$ROOT/evidence"
cd "$ROOT"

if [[ ! -s "$RUNTIME/api_token" ]]; then
  python3 - <<'PY'
from pathlib import Path
import os, secrets
p=Path('/kaggle/working/Z-Image-Turbo-Kaggle-T4x2-REST-Server/.runtime/api_token')
p.write_text(secrets.token_urlsafe(32), encoding='utf-8')
os.chmod(p, 0o600)
PY
fi

if ! python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8101/health',timeout=2)" >/dev/null 2>&1; then
  PYTHONPATH=src nohup python3 -m uvicorn zimage_server.worker_api:app --host 127.0.0.1 --port 8101 --log-level info >logs/worker.log 2>&1 &
  echo $! > "$RUNTIME/worker.pid"
fi

python3 - <<'PY'
import json, time, urllib.error, urllib.request
end=time.time()+900
last=None
while time.time()<end:
 try:
  with urllib.request.urlopen('http://127.0.0.1:8101/health',timeout=2) as r:
   state=json.load(r)
   status=state.get('status')
   if status != last:
    print(f"WORKER_STATUS={status}", flush=True)
    last=status
   if status == 'ready':
    with urllib.request.urlopen('http://127.0.0.1:8101/ready',timeout=2) as rr:
     json.load(rr)
    break
   if status == 'error':
    raise SystemExit('WORKER_LOAD_ERROR: '+json.dumps(state))
 except urllib.error.URLError:
  pass
 time.sleep(2)
else:
 import subprocess
 subprocess.run(['bash','-lc','echo WORKER_DIAGNOSTICS_START; tail -n 120 logs/worker.log 2>/dev/null || true; nvidia-smi || true; echo WORKER_DIAGNOSTICS_END'])
 raise SystemExit('WORKER_READY_TIMEOUT')
print('WORKER_READY=PASS')
PY

if ! python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8090/health',timeout=2)" >/dev/null 2>&1; then
  TOKEN="$(cat "$RUNTIME/api_token")"
  ZIMAGE_API_TOKEN="$TOKEN" PYTHONPATH=src nohup python3 -m uvicorn zimage_server.app:app --host 127.0.0.1 --port 8090 --log-level info >logs/coordinator.log 2>&1 &
  echo $! > "$RUNTIME/coordinator.pid"
fi
sleep 1
python3 scripts/local_control_acceptance.py >/dev/null
printf 'ZIMAGE_SERVER_READY=PASS\nLOCAL_URL=http://127.0.0.1:8090/\nTOKEN_FILE=%s\n' "$RUNTIME/api_token"
