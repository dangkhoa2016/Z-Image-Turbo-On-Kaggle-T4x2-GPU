import json
import os
import time
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8090"
ROOT = Path("/kaggle/working/Z-Image-Turbo-Kaggle-T4x2-REST-Server")
TOKEN = (ROOT / ".runtime" / "api_token").read_text().strip()
AUTH = {"Authorization": "Bearer " + TOKEN}
JSON_HEADERS = {**AUTH, "Content-Type": "application/json"}
PROMPT = "A cinematic futuristic library floating above a calm ocean at sunrise, warm volumetric light, intricate architecture, realistic reflections, highly detailed"
LIVE_EVENTS = os.environ.get("ZIMAGE_NOTEBOOK_EVENTS") == "1"


def emit_event(event, **payload):
    if LIVE_EVENTS:
        print("NOTEBOOK_EVENT\t" + json.dumps({"event": event, **payload}, separators=(",", ":")), flush=True)


def submit(seed):
    payload = {"prompt": PROMPT, "seed": seed, "profile": "safe_512"}
    req = urllib.request.Request(BASE + "/v1/images/generations", data=json.dumps(payload).encode(), headers=JSON_HEADERS, method="POST")
    with urllib.request.urlopen(req, timeout=10) as response:
        assert response.status == 202
        return json.load(response)["id"]


def get_job(job_id):
    req = urllib.request.Request(BASE + "/v1/jobs/" + job_id, headers=AUTH)
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.load(response)

ids = [submit(seed) for seed in range(1001, 1006)]
time.sleep(1)
initial = [get_job(jid) for jid in ids]
assert sum(j["status"] == "running" for j in initial) <= 1, initial
assert all(j["status"] in {"queued", "running", "complete"} for j in initial)

results = []
for index, jid in enumerate(ids, start=1):
    deadline = time.monotonic() + 420
    while True:
        job = get_job(jid)
        if job["status"] in {"complete", "error"}:
            break
        if time.monotonic() > deadline:
            raise TimeoutError(jid)
        time.sleep(1)
    assert job["status"] == "complete", job
    results.append(job)
    result = job["result"]
    image_req = urllib.request.Request(BASE + "/v1/jobs/" + jid + "/image", headers=AUTH)
    with urllib.request.urlopen(image_req, timeout=10) as response:
        image_bytes = response.read()
    assert image_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    (ROOT / "outputs").mkdir(parents=True, exist_ok=True)
    image_rel = f"outputs/endurance-{index:02d}-seed-{result['seed']}.png"
    (ROOT / image_rel).write_bytes(image_bytes)
    emit_event(
        "job_complete",
        index=index,
        total=len(ids),
        job_id=jid,
        profile=result["profile"],
        seed=result["seed"],
        inference_seconds=result["inference_seconds"],
        sha256=result["sha256"],
        width=result["width"],
        height=result["height"],
        image_path=image_rel,
    )

for previous, current in zip(results, results[1:]):
    assert current["started_at"] >= previous["finished_at"], (previous, current)

summary = []
for job in results:
    r = job["result"]
    summary.append({
        "id": job["id"],
        "seed": r["seed"],
        "submitted_at": job["submitted_at"],
        "started_at": job["started_at"],
        "finished_at": job["finished_at"],
        "inference_seconds": r["inference_seconds"],
        "sha256": r["sha256"],
        "gpu0_allocated_before": r["memory_before"]["gpu0"]["allocated"],
        "gpu0_allocated_after": r["memory_after"]["gpu0"]["allocated"],
        "gpu1_allocated_before": r["memory_before"]["gpu1"]["allocated"],
        "gpu1_allocated_after": r["memory_after"]["gpu1"]["allocated"],
        "gpu0_peak_allocated": r["memory_after"]["gpu0"]["peak_allocated"],
        "gpu1_peak_allocated": r["memory_after"]["gpu1"]["peak_allocated"],
    })

assert all(x["gpu0_allocated_after"] == summary[0]["gpu0_allocated_after"] for x in summary)
assert all(x["gpu1_allocated_after"] == summary[0]["gpu1_allocated_after"] for x in summary)
Path("evidence/endurance-5jobs.json").write_text(json.dumps({"initial_states": [j["status"] for j in initial], "jobs": summary}, indent=2), encoding="utf-8")
print(json.dumps({"initial_states": [j["status"] for j in initial], "jobs": summary}, indent=2))
print("QUEUE_SERIALIZATION=PASS")
print("FIVE_JOB_ENDURANCE=PASS")
print("MEMORY_STABILITY_512=PASS")
