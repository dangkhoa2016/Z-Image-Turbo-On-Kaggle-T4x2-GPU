import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path("/kaggle/working/Z-Image-Turbo-Kaggle-T4x2-REST-Server")
BASE = (ROOT / ".runtime" / "tunnel_url").read_text().strip()
TOKEN = (ROOT / ".runtime" / "api_token").read_text().strip()
AUTH = {"Authorization": "Bearer " + TOKEN}
JSON_HEADERS = {**AUTH, "Content-Type": "application/json"}


def get(path, headers=None):
    req = urllib.request.Request(BASE + path, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return response.status, response.read(), response.headers.get_content_type()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), exc.headers.get_content_type()

status, body, content_type = get("/")
root = json.loads(body)
assert status == 200 and content_type == "application/json"
assert root["type"] == "rest-api" and root["service"] == "z-image-turbo-kaggle-t4x2"
status, body, _ = get("/health")
assert status == 200 and json.loads(body)["status"] == "ok"
status, body, _ = get("/ready")
assert status == 401
status, body, _ = get("/ready", AUTH)
assert status == 200 and json.loads(body)["ready"] is True

payload = {"prompt": "A cinematic coastal observatory at sunrise, realistic reflections, volumetric light, intricate architecture", "seed": 3001, "profile": "safe_512"}
req = urllib.request.Request(BASE + "/v1/images/generations", data=json.dumps(payload).encode(), headers=JSON_HEADERS, method="POST")
with urllib.request.urlopen(req, timeout=20) as response:
    submitted = json.load(response)
assert submitted["status"] == "queued"
job_id = submitted["id"]

deadline = time.monotonic() + 180
while True:
    status, body, _ = get("/v1/jobs/" + job_id, AUTH)
    assert status == 200
    job = json.loads(body)
    if job["status"] in {"complete", "error"}:
        break
    if time.monotonic() > deadline:
        raise TimeoutError(job_id)
    time.sleep(1)
assert job["status"] == "complete", job
status, image, content_type = get("/v1/jobs/" + job_id + "/image", AUTH)
assert status == 200 and content_type == "image/png" and image.startswith(b"\x89PNG\r\n\x1a\n")
summary = {"public_url": BASE, "job_id": job_id, "inference_seconds": job["result"]["inference_seconds"], "sha256": job["result"]["sha256"], "png_bytes": len(image), "verdict": "PASS"}
(ROOT / "evidence" / "public-tunnel-acceptance.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
print("PUBLIC_TUNNEL_ACCEPTANCE=PASS")
