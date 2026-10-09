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


def test_official_kaggle_saved_version_acceptance_is_curated():
    official = load("official-kaggle-saved-version.json")
    assert official["source"] == "official_kaggle_saved_version"
    assert official["source_notebook_sha256"] == "1aeaefb88b325ac068f996e7f1e6aaaf5f6e73e1fcf5b6de363d3426bd129d33"
    assert official["executed_notebook_sha256"] == "488f881fbcd006e40de529d1e8c27a76f869a5370b0c97e4fcc3f3d041976599"
    assert official["cells"] == {"total": 25, "code": 11, "executed": 11, "errors": 0, "embedded_png": 9}
    assert official["parallel_loading"] == {"enabled": True, "workers": 4}
    assert official["model_load_seconds"] == 124.084353364
    assert official["golden_sha256"] == "56e0fca007d3da945de77788b5ab8a0a131b58730d93b624ca65e7c6ca6ea307"
    assert official["required_markers"] == {
        "PREFLIGHT": "PASS",
        "WORKER_READY": "PASS",
        "GOLDEN_512_DETERMINISM": "PASS",
        "QUEUE_ENDURANCE": "PASS",
        "ERROR_BOUNDARIES": "PASS",
        "MIXED_PROFILE_QUALIFICATION": "PASS",
        "EVIDENCE_VERIFY": "PASS",
        "FINAL_QUALIFICATION": "PASS",
    }
    assert official["public_https_rest_acceptance"] == "SKIPPED_OPTIONAL"
    assert official["verdict"] == "PASS"


def test_release_acceptance_verifier_accepts_official_saved_version():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify_release_acceptance.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "RELEASE_ACCEPTANCE_VERIFY=PASS" in result.stdout
