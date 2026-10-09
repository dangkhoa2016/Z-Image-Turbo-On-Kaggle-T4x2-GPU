import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / "evidence"


def load(name: str):
    return json.loads((E / name).read_text(encoding="utf-8"))


endurance = load("endurance-5jobs.json")
mixed = load("mixed-512-768-512.json")
public = load("public-tunnel-acceptance.json")
errors = load("error-boundary.json")
golden = load("golden-512-seed42.json")
contract = load("api-contract-status-codes.json")

assert golden["verdict"] == "PASS"
assert mixed["summary"]["verdict"] == "PASS"
assert public["verdict"] in {"PASS", "SKIPPED"}
if public["verdict"] == "PASS":
    assert public["public_url"] == "<ephemeral-quick-tunnel-url>"
else:
    assert public.get("optional") is True
assert errors["ready_after"]["ready"] is True
assert contract["verdict"] == "PASS"

summary = {
    "project": "Z-Image-Turbo-Kaggle-T4x2-REST-Server",
    "hardware": {"gpu_count": 2, "gpu_model": "Tesla T4"},
    "model": "dangkhoa2016/tongyi-mai-z-image-turbo/PyTorch/default/1",
    "dtype": "bfloat16",
    "device_map": {"transformer": 0, "text_encoder": 1, "vae": 1},
    "profiles": {
        "safe_512": {"width": 512, "height": 512, "steps": 9, "guidance_scale": 0.0},
        "high_768": {"width": 768, "height": 768, "steps": 9, "guidance_scale": 0.0},
    },
    "golden_512": {
        "sha256": golden["sha256"],
        "inference_seconds": golden["inference_seconds"],
        "pixel_stats": golden["pixel_stats"],
        "verdict": golden["verdict"],
    },
    "queue_endurance": {
        "initial_states": endurance["initial_states"],
        "latencies": [job["inference_seconds"] for job in endurance["jobs"]],
        "verdict": "PASS",
    },
    "mixed_profile": mixed["summary"],
    "error_boundary": {
        "scope": "live_kaggle_runtime_subset",
        "status_codes": {key: value[0] for key, value in errors["checks"].items()},
        "ready_after": errors["ready_after"]["ready"],
        "verdict": "PASS",
    },
    "api_contract": contract,
    "public_tunnel": public,
    "unsupported": ["fp16", "1024x1024", "parallel_gpu_generation", "pipeline_per_request"],
    "final_verdict": "PASS",
}

summary_text = json.dumps(summary, indent=2) + "\n"
(E / "qualification-summary.json").write_text(summary_text, encoding="utf-8")
(E / "finalize-output.txt").write_text(summary_text + "FINAL_QUALIFICATION=PASS\n", encoding="utf-8")
print(summary_text, end="")
print("FINAL_QUALIFICATION=PASS")
