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
PROMPT = "A cinematic glass observatory above a quiet alpine lake at sunrise, realistic reflections, volumetric light, intricate architecture, highly detailed"
LIVE_EVENTS = os.environ.get("ZIMAGE_NOTEBOOK_EVENTS") == "1"


def emit_event(event, **payload):
    if LIVE_EVENTS:
        print("NOTEBOOK_EVENT\t" + json.dumps({"event": event, **payload}, separators=(",", ":")), flush=True)


def run(profile, seed):
    payload = {"prompt": PROMPT, "seed": seed, "profile": profile}
    req = urllib.request.Request(BASE + "/v1/images/generations", data=json.dumps(payload).encode(), headers=JSON_HEADERS, method="POST")
    with urllib.request.urlopen(req, timeout=10) as response:
        submitted = json.load(response)
    jid = submitted["id"]
    deadline = time.monotonic() + 300
    while True:
        req = urllib.request.Request(BASE + "/v1/jobs/" + jid, headers=AUTH)
        with urllib.request.urlopen(req, timeout=10) as response:
            job = json.load(response)
        if job["status"] in {"complete", "error"}:
            break
        if time.monotonic() > deadline:
            raise TimeoutError(jid)
        time.sleep(1)
    assert job["status"] == "complete", job
    result = job["result"]
    return {
        "request_id": jid,
        "profile": profile,
        "seed": seed,
        "inference_seconds": result["inference_seconds"],
        "sha256": result["sha256"],
        "memory_before": result["memory_before"],
        "memory_after": result["memory_after"],
    }


runs = []
sequence = [("safe_512", 2001), ("high_768", 2002), ("safe_512", 2003)]
for index, (profile, seed) in enumerate(sequence, start=1):
    item = run(profile, seed)
    runs.append(item)
    image_req = urllib.request.Request(BASE + "/v1/jobs/" + item["request_id"] + "/image", headers=AUTH)
    with urllib.request.urlopen(image_req, timeout=10) as response:
        image_bytes = response.read()
    assert image_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    (ROOT / "outputs").mkdir(parents=True, exist_ok=True)
    image_rel = f"outputs/mixed-{index:02d}-{profile}-seed-{seed}.png"
    (ROOT / image_rel).write_bytes(image_bytes)
    emit_event(
        "mixed_complete",
        index=index,
        total=len(sequence),
        job_id=item["request_id"],
        profile=profile,
        seed=seed,
        inference_seconds=item["inference_seconds"],
        sha256=item["sha256"],
        width=512 if profile == "safe_512" else 768,
        height=512 if profile == "safe_512" else 768,
        image_path=image_rel,
    )
first, high, final = runs
warmup_limit = 16 * 1024 * 1024
for gpu in ("gpu0", "gpu1"):
    first_delta = first["memory_after"][gpu]["allocated"] - first["memory_before"][gpu]["allocated"]
    assert 0 <= first_delta <= warmup_limit
    assert high["memory_after"][gpu]["allocated"] == high["memory_before"][gpu]["allocated"]
    assert final["memory_after"][gpu]["allocated"] == final["memory_before"][gpu]["allocated"]
    assert final["memory_after"][gpu]["allocated"] == high["memory_after"][gpu]["allocated"]
    assert final["memory_after"][gpu]["reserved"] == high["memory_after"][gpu]["reserved"]

summary = {
    "sequence": [r["profile"] for r in runs],
    "latencies": [r["inference_seconds"] for r in runs],
    "sha256": [r["sha256"] for r in runs],
    "gpu0_peak_reserved_768": high["memory_after"]["gpu0"]["peak_reserved"],
    "gpu1_peak_reserved_768": high["memory_after"]["gpu1"]["peak_reserved"],
    "gpu0_final_allocated": final["memory_after"]["gpu0"]["allocated"],
    "gpu1_final_allocated": final["memory_after"]["gpu1"]["allocated"],
    "gpu0_final_reserved": final["memory_after"]["gpu0"]["reserved"],
    "gpu1_final_reserved": final["memory_after"]["gpu1"]["reserved"],
    "verdict": "PASS",
}
record = {"summary": summary, "runs": runs}
(ROOT / "evidence" / "mixed-512-768-512.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))
print("HIGH_768_ACCEPTANCE=PASS")
print("MIXED_PROFILE_MEMORY_STABILITY=PASS")
