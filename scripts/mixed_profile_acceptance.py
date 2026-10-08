import json
import time
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8090"
TOKEN = Path("/kaggle/working/Z-Image-Turbo-Kaggle-T4x2-REST-Server/.runtime/api_token").read_text().strip()
AUTH = {"Authorization": "Bearer " + TOKEN}
JSON_HEADERS = {**AUTH, "Content-Type": "application/json"}
PROMPT = "A cinematic glass observatory above a quiet alpine lake at sunrise, realistic reflections, volumetric light, intricate architecture, highly detailed"


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
    r = job["result"]
    return {
        "id": jid,
        "profile": profile,
        "seed": seed,
        "inference_seconds": r["inference_seconds"],
        "sha256": r["sha256"],
        "memory_before": r["memory_before"],
        "memory_after": r["memory_after"],
    }

runs = [run("safe_512", 2001), run("high_768", 2002), run("safe_512", 2003)]
for run_result in runs:
    for gpu in ("gpu0", "gpu1"):
        assert run_result["memory_after"][gpu]["allocated"] == run_result["memory_before"][gpu]["allocated"]

assert runs[2]["memory_after"]["gpu0"]["allocated"] == runs[0]["memory_after"]["gpu0"]["allocated"]
assert runs[2]["memory_after"]["gpu1"]["allocated"] == runs[0]["memory_after"]["gpu1"]["allocated"]

Path("evidence/mixed-512-768-512.json").write_text(json.dumps({"runs": runs}, indent=2), encoding="utf-8")
print(json.dumps({"runs": runs}, indent=2))
print("HIGH_768_ACCEPTANCE=PASS")
print("MIXED_PROFILE_MEMORY_STABILITY=PASS")
