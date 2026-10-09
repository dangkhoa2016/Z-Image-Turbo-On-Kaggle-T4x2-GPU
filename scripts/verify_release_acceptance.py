import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
NOTEBOOK = ROOT / "notebooks" / "kaggle-t4x2-rest-server-production.ipynb"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_SOURCE_NOTEBOOK_SHA256 = "1aeaefb88b325ac068f996e7f1e6aaaf5f6e73e1fcf5b6de363d3426bd129d33"
EXPECTED_EXECUTED_NOTEBOOK_SHA256 = "488f881fbcd006e40de529d1e8c27a76f869a5370b0c97e4fcc3f3d041976599"
EXPECTED_GOLDEN_SHA256 = "56e0fca007d3da945de77788b5ab8a0a131b58730d93b624ca65e7c6ca6ea307"
EXPECTED_MARKERS = {
    "PREFLIGHT": "PASS",
    "WORKER_READY": "PASS",
    "GOLDEN_512_DETERMINISM": "PASS",
    "QUEUE_ENDURANCE": "PASS",
    "ERROR_BOUNDARIES": "PASS",
    "MIXED_PROFILE_QUALIFICATION": "PASS",
    "EVIDENCE_VERIFY": "PASS",
    "FINAL_QUALIFICATION": "PASS",
}


def load(name: str):
    path = EVIDENCE / name
    assert path.is_file(), f"missing evidence file: {name}"
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    official = load("official-kaggle-saved-version.json")
    golden = load("golden-512-seed42.json")
    public = load("public-tunnel-acceptance.json")

    assert official["source"] == "official_kaggle_saved_version"
    assert official["date_utc"] == "2026-10-09"
    assert SHA256.fullmatch(official["source_notebook_sha256"])
    assert SHA256.fullmatch(official["executed_notebook_sha256"])
    assert official["source_notebook_sha256"] == EXPECTED_SOURCE_NOTEBOOK_SHA256
    assert sha256(NOTEBOOK) == EXPECTED_SOURCE_NOTEBOOK_SHA256
    assert official["executed_notebook_sha256"] == EXPECTED_EXECUTED_NOTEBOOK_SHA256
    assert official["cells"] == {
        "total": 25,
        "code": 11,
        "executed": 11,
        "errors": 0,
        "embedded_png": 9,
    }
    assert official["parallel_loading"] == {"enabled": True, "workers": 4}
    assert official["model_load_seconds"] == 124.084353364
    assert official["golden_sha256"] == EXPECTED_GOLDEN_SHA256
    assert official["golden_sha256"] == golden["sha256"]
    assert official["required_markers"] == EXPECTED_MARKERS
    assert official["public_https_rest_acceptance"] == "SKIPPED_OPTIONAL"
    assert public["verdict"] in {"PASS", "SKIPPED"}
    if public["verdict"] == "SKIPPED":
        assert public.get("optional") is True
    assert official["verdict"] == "PASS"

    print(json.dumps({
        "source_notebook_sha256": official["source_notebook_sha256"],
        "executed_notebook_sha256": official["executed_notebook_sha256"],
        "model_load_seconds": official["model_load_seconds"],
        "golden_sha256": official["golden_sha256"],
        "verdict": "PASS",
    }, indent=2))
    print("RELEASE_ACCEPTANCE_VERIFY=PASS")


if __name__ == "__main__":
    main()
