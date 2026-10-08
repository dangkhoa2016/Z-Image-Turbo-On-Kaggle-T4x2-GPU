import json
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8090"
TOKEN_FILE = Path("/kaggle/working/Z-Image-Turbo-Kaggle-T4x2-REST-Server/.runtime/api_token")
TOKEN = TOKEN_FILE.read_text(encoding="utf-8").strip()


def get(path, authenticated=False):
    headers = {"Authorization": "Bearer " + TOKEN} if authenticated else {}
    req = urllib.request.Request(BASE + path, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            body = json.loads(response.read().decode("utf-8"))
            return response.status, body
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


checks = {}
checks["health"] = get("/health")
checks["ready_without_auth"] = get("/ready")
checks["ready"] = get("/ready", True)
checks["info"] = get("/v1/info", True)

assert checks["health"][0] == 200
assert checks["ready_without_auth"][0] == 401
assert checks["ready"][0] == 200 and checks["ready"][1]["ready"] is True
assert checks["info"][0] == 200
print(json.dumps(checks, indent=2))
print("CONTROL_PLANE_ACCEPTANCE=PASS")
