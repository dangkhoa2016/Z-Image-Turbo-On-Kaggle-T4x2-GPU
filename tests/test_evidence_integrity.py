import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"


def load(name: str):
    return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))


def test_public_tunnel_record_is_canonical_everywhere():
    public = load("public-tunnel-acceptance.json")
    summary = load("qualification-summary.json")
    finalize_text = (EVIDENCE / "finalize-output.txt").read_text(encoding="utf-8")
    finalize_json = json.loads(finalize_text.split("\nFINAL_QUALIFICATION=PASS", 1)[0])

    assert summary["public_tunnel"] == public
    assert finalize_json["public_tunnel"] == public


def test_live_error_boundary_remains_runtime_scoped():
    errors = load("error-boundary.json")
    assert {key: value[0] for key, value in errors["checks"].items()} == {
        "missing_auth": 401,
        "invalid_auth": 403,
        "blank_prompt": 422,
        "unsupported_1024": 422,
    }
    assert errors["ready_after"]["ready"] is True


def test_api_contract_evidence_covers_documented_status_codes():
    contract = load("api-contract-status-codes.json")
    assert contract["source"] == "cpu_fastapi_contract_test"
    assert contract["status_codes"] == {
        "missing_auth": 401,
        "invalid_auth": 403,
        "unknown_job": 404,
        "image_before_complete": 409,
        "blank_prompt": 422,
        "unsupported_1024": 422,
        "queue_full": 429,
        "worker_unavailable": 503,
    }
    assert contract["verdict"] == "PASS"


def test_golden_512_has_curated_evidence_record():
    golden = load("golden-512-seed42.json")
    summary = load("qualification-summary.json")
    assert golden["sha256"] == summary["golden_512"]["sha256"]
    assert golden["inference_seconds"] == summary["golden_512"]["inference_seconds"]
    assert golden["pixel_stats"] == summary["golden_512"]["pixel_stats"]
    assert golden["verdict"] == "PASS"


def test_evidence_verifier_accepts_repository_bundle():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_evidence.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "EVIDENCE_VERIFY=PASS" in result.stdout
