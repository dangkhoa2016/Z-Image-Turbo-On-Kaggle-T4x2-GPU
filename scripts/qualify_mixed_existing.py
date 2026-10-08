import glob
import json
import os
from pathlib import Path

ROOT = Path("/kaggle/working/Z-Image-Turbo-Kaggle-T4x2-REST-Server")
records = []
for path in glob.glob(str(ROOT / "metadata" / "*.json")):
    data = json.load(open(path, encoding="utf-8"))
    if data.get("seed") in {2001, 2002, 2003}:
        records.append(data)
records.sort(key=lambda x: x["seed"])
assert [r["seed"] for r in records] == [2001, 2002, 2003]
assert [r["profile"] for r in records] == ["safe_512", "high_768", "safe_512"]

first, high, final = records
warmup_limit = 16 * 1024 * 1024
for gpu in ("gpu0", "gpu1"):
    first_delta = first["memory_after"][gpu]["allocated"] - first["memory_before"][gpu]["allocated"]
    assert 0 <= first_delta <= warmup_limit
    assert high["memory_after"][gpu]["allocated"] == high["memory_before"][gpu]["allocated"]
    assert final["memory_after"][gpu]["allocated"] == final["memory_before"][gpu]["allocated"]
    assert final["memory_after"][gpu]["allocated"] == high["memory_after"][gpu]["allocated"]
    assert final["memory_after"][gpu]["reserved"] == high["memory_after"][gpu]["reserved"]

summary = {
    "sequence": ["safe_512", "high_768", "safe_512"],
    "latencies": [r["inference_seconds"] for r in records],
    "sha256": [r["sha256"] for r in records],
    "gpu0_peak_reserved_768": high["memory_after"]["gpu0"]["peak_reserved"],
    "gpu1_peak_reserved_768": high["memory_after"]["gpu1"]["peak_reserved"],
    "gpu0_final_allocated": final["memory_after"]["gpu0"]["allocated"],
    "gpu1_final_allocated": final["memory_after"]["gpu1"]["allocated"],
    "gpu0_final_reserved": final["memory_after"]["gpu0"]["reserved"],
    "gpu1_final_reserved": final["memory_after"]["gpu1"]["reserved"],
    "verdict": "PASS",
}
(ROOT / "evidence" / "mixed-512-768-512.json").write_text(json.dumps({"summary": summary, "runs": records}, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
print("HIGH_768_ACCEPTANCE=PASS")
print("MIXED_PROFILE_MEMORY_STABILITY=PASS")
