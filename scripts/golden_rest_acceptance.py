import json
import time
import urllib.request
from pathlib import Path

ROOT = Path("/kaggle/working/Z-Image-Turbo-Kaggle-T4x2-REST-Server")
BASE = "http://127.0.0.1:8090"
TOKEN = (ROOT / ".runtime" / "api_token").read_text().strip()
HEADERS = {"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"}
EXPECTED_SHA = "56e0fca007d3da945de77788b5ab8a0a131b58730d93b624ca65e7c6ca6ea307"
PROMPT = "A cinematic photograph of a small futuristic library floating above a calm ocean at sunrise, warm volumetric light, intricate architecture, realistic reflections, highly detailed"

payload = {"prompt": PROMPT, "seed": 42, "profile": "safe_512"}
req = urllib.request.Request(BASE + "/v1/images/generations", data=json.dumps(payload).encode(), headers=HEADERS, method="POST")
with urllib.request.urlopen(req, timeout=10) as response:
    submitted = json.load(response)
assert submitted["status"] == "queued"
job_id = submitted["id"]

started = time.monotonic()
while True:
    req = urllib.request.Request(BASE + "/v1/jobs/" + job_id, headers={"Authorization": "Bearer " + TOKEN})
    with urllib.request.urlopen(req, timeout=10) as response:
        job = json.load(response)
    if job["status"] in {"complete", "error"}:
        break
    if time.monotonic() - started > 180:
        raise TimeoutError(job_id)
    time.sleep(1)

assert job["status"] == "complete", job
result = job["result"]
assert result["sha256"] == EXPECTED_SHA, result["sha256"]
image_req = urllib.request.Request(BASE + "/v1/jobs/" + job_id + "/image", headers={"Authorization": "Bearer " + TOKEN})
with urllib.request.urlopen(image_req, timeout=10) as response:
    image_bytes = response.read()
assert image_bytes.startswith(b"\x89PNG\r\n\x1a\n")
(ROOT / "outputs").mkdir(parents=True, exist_ok=True)
(ROOT / "outputs" / "golden-512-seed42.png").write_bytes(image_bytes)

record = {
    "profile": result["profile"],
    "seed": result["seed"],
    "width": result["width"],
    "height": result["height"],
    "steps": result["steps"],
    "guidance_scale": result["guidance_scale"],
    "dtype": result["dtype"],
    "inference_seconds": result["inference_seconds"],
    "sha256": result["sha256"],
    "pixel_stats": result["pixel_stats"],
    "verdict": "PASS",
}
(ROOT / "evidence" / "golden-512-seed42.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps({**record, "png_bytes": len(image_bytes)}, indent=2))
print("GOLDEN_REST_ACCEPTANCE=PASS")
