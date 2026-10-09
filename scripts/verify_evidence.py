import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / "evidence"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
PLACEHOLDER = "<ephemeral-quick-tunnel-url>"


def load(name: str):
    path = E / name
    assert path.is_file(), f"missing evidence file: {name}"
    return json.loads(path.read_text(encoding="utf-8"))


def assert_sha(value: str, label: str) -> None:
    assert SHA256.fullmatch(value), f"invalid SHA-256 for {label}: {value!r}"


def main() -> None:
    endurance = load("endurance-5jobs.json")
    errors = load("error-boundary.json")
    golden = load("golden-512-seed42.json")
    contract = load("api-contract-status-codes.json")
    mixed = load("mixed-512-768-512.json")
    public = load("public-tunnel-acceptance.json")
    summary = load("qualification-summary.json")

    final_text = (E / "finalize-output.txt").read_text(encoding="utf-8")
    marker = "\nFINAL_QUALIFICATION=PASS\n"
    assert final_text.endswith(marker), "finalize-output.txt missing PASS marker"
    final_json = json.loads(final_text[: -len(marker) + 1])
    assert final_json == summary, "finalize-output.txt JSON differs from qualification-summary.json"

    assert golden["verdict"] == "PASS"
    assert golden["profile"] == "safe_512" and golden["seed"] == 42
    assert (golden["width"], golden["height"], golden["steps"], golden["guidance_scale"]) == (512, 512, 9, 0.0)
    assert golden["dtype"] == "bfloat16"
    assert_sha(golden["sha256"], "golden_512")
    assert summary["golden_512"] == {
        "sha256": golden["sha256"],
        "inference_seconds": golden["inference_seconds"],
        "pixel_stats": golden["pixel_stats"],
        "verdict": golden["verdict"],
    }

    assert endurance["initial_states"] == ["running", "queued", "queued", "queued", "queued"]
    assert len(endurance["jobs"]) == 5
    for index, job in enumerate(endurance["jobs"]):
        assert_sha(job["sha256"], f"endurance[{index}]")
    assert summary["queue_endurance"]["initial_states"] == endurance["initial_states"]
    assert summary["queue_endurance"]["latencies"] == [job["inference_seconds"] for job in endurance["jobs"]]
    assert summary["queue_endurance"]["verdict"] == "PASS"

    runs = mixed["runs"]
    mixed_summary = mixed["summary"]
    assert len(runs) == 3
    assert [run["profile"] for run in runs] == ["safe_512", "high_768", "safe_512"]
    assert mixed_summary["sequence"] == [run["profile"] for run in runs]
    assert mixed_summary["latencies"] == [run["inference_seconds"] for run in runs]
    assert mixed_summary["sha256"] == [run["sha256"] for run in runs]
    for index, run in enumerate(runs):
        assert_sha(run["sha256"], f"mixed[{index}]")
    high, final = runs[1], runs[2]
    assert mixed_summary["gpu0_peak_reserved_768"] == high["memory_after"]["gpu0"]["peak_reserved"]
    assert mixed_summary["gpu1_peak_reserved_768"] == high["memory_after"]["gpu1"]["peak_reserved"]
    assert mixed_summary["gpu0_final_allocated"] == final["memory_after"]["gpu0"]["allocated"]
    assert mixed_summary["gpu1_final_allocated"] == final["memory_after"]["gpu1"]["allocated"]
    assert mixed_summary["gpu0_final_reserved"] == final["memory_after"]["gpu0"]["reserved"]
    assert mixed_summary["gpu1_final_reserved"] == final["memory_after"]["gpu1"]["reserved"]
    assert mixed_summary["verdict"] == "PASS"
    assert summary["mixed_profile"] == mixed_summary

    live_statuses = {key: value[0] for key, value in errors["checks"].items()}
    assert live_statuses == {
        "missing_auth": 401,
        "invalid_auth": 403,
        "blank_prompt": 422,
        "unsupported_1024": 422,
    }
    assert errors["ready_after"]["ready"] is True
    assert summary["error_boundary"] == {
        "scope": "live_kaggle_runtime_subset",
        "status_codes": live_statuses,
        "ready_after": True,
        "verdict": "PASS",
    }

    expected_contract = {
        "missing_auth": 401,
        "invalid_auth": 403,
        "unknown_job": 404,
        "image_before_complete": 409,
        "blank_prompt": 422,
        "unsupported_1024": 422,
        "queue_full": 429,
        "worker_unavailable": 503,
    }
    assert contract["source"] == "cpu_fastapi_contract_test"
    assert contract["scope"] == "coordinator_http_contract_without_gpu_inference"
    assert contract["status_codes"] == expected_contract
    assert contract["verdict"] == "PASS"
    assert summary["api_contract"] == contract

    assert public["verdict"] in {"PASS", "SKIPPED"}
    if public["verdict"] == "PASS":
        assert public["public_url"] == PLACEHOLDER
        assert_sha(public["sha256"], "public_tunnel")
    else:
        assert public.get("optional") is True
        assert public.get("reason")
    assert summary["public_tunnel"] == public

    corpus = "\n".join(path.read_text(encoding="utf-8") for path in E.iterdir() if path.is_file())
    assert "trycloudflare.com" not in corpus
    assert not re.search(r"Authorization:\s*Bearer\s+[A-Za-z0-9._-]{20,}", corpus)
    assert summary["final_verdict"] == "PASS"

    print(json.dumps({"files": len([p for p in E.iterdir() if p.is_file()]), "verdict": "PASS"}, indent=2))
    print("EVIDENCE_VERIFY=PASS")


if __name__ == "__main__":
    main()
