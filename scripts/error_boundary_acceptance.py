import json
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8090"
TOKEN = Path("/kaggle/working/Z-Image-Turbo-Kaggle-T4x2-REST-Server/.runtime/api_token").read_text().strip()
AUTH = {"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"}


def post(payload, headers):
    req = urllib.request.Request(BASE + "/v1/images/generations", data=json.dumps(payload).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode())

checks = {}
checks["missing_auth"] = post({"prompt": "test", "seed": 1, "profile": "safe_512"}, {"Content-Type": "application/json"})
checks["invalid_auth"] = post({"prompt": "test", "seed": 1, "profile": "safe_512"}, {"Authorization": "Bearer invalid-session-token", "Content-Type": "application/json"})
checks["blank_prompt"] = post({"prompt": "   ", "seed": 1, "profile": "safe_512"}, AUTH)
checks["unsupported_1024"] = post({"prompt": "test", "seed": 1, "profile": "high_1024"}, AUTH)

assert checks["missing_auth"][0] == 401
assert checks["invalid_auth"][0] == 403
assert checks["blank_prompt"][0] == 422
assert checks["unsupported_1024"][0] == 422

req = urllib.request.Request(BASE + "/ready", headers={"Authorization": "Bearer " + TOKEN})
with urllib.request.urlopen(req, timeout=10) as response:
    ready = json.load(response)
assert ready["ready"] is True

Path("evidence/error-boundary.json").write_text(json.dumps({"checks": checks, "ready_after": ready}, indent=2), encoding="utf-8")
print(json.dumps({"status_codes": {k: v[0] for k, v in checks.items()}, "ready_after": ready["ready"]}, indent=2))
print("ERROR_BOUNDARY_ACCEPTANCE=PASS")
