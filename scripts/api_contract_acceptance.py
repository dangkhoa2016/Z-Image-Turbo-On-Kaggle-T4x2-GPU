import json
import os
import threading
import time
from pathlib import Path

from fastapi.testclient import TestClient

os.environ.setdefault("ZIMAGE_API_TOKEN", "contract-test-token-abcdefghijklmnopqrstuvwxyz")

from zimage_server.app import create_app

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "api-contract-status-codes.json"
EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
TOKEN = os.environ["ZIMAGE_API_TOKEN"]
AUTH = {"Authorization": "Bearer " + TOKEN}
VALID = {"prompt": "contract test", "seed": 1, "profile": "safe_512"}


def wait_for_status(client: TestClient, job_id: str, expected: str) -> None:
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        response = client.get(f"/v1/jobs/{job_id}", headers=AUTH)
        if response.status_code == 200 and response.json()["status"] == expected:
            return
        time.sleep(0.01)
    raise AssertionError(f"job {job_id} did not reach {expected}")


def main() -> None:
    gate = threading.Event()

    def blocking_runner(_payload):
        if not gate.wait(timeout=5):
            raise TimeoutError("contract-test gate timed out")
        return {"output_path": "/tmp/contract-test.png", "sha256": "0" * 64, "inference_seconds": 0.0}

    status_codes = {}
    app = create_app(start_worker=True, runner=blocking_runner, max_queue_size=1)
    try:
        with TestClient(app) as client:
            status_codes["missing_auth"] = client.post("/v1/images/generations", json=VALID).status_code
            status_codes["invalid_auth"] = client.post(
                "/v1/images/generations",
                headers={"Authorization": "Bearer wrong"},
                json=VALID,
            ).status_code
            status_codes["blank_prompt"] = client.post(
                "/v1/images/generations", headers=AUTH, json={**VALID, "prompt": "   "}
            ).status_code
            status_codes["unsupported_1024"] = client.post(
                "/v1/images/generations", headers=AUTH, json={**VALID, "profile": "high_1024"}
            ).status_code
            status_codes["unknown_job"] = client.get("/v1/jobs/img_missing", headers=AUTH).status_code

            first = client.post("/v1/images/generations", headers=AUTH, json=VALID)
            assert first.status_code == 202
            first_id = first.json()["id"]
            wait_for_status(client, first_id, "running")
            status_codes["image_before_complete"] = client.get(
                f"/v1/jobs/{first_id}/image", headers=AUTH
            ).status_code

            second = client.post("/v1/images/generations", headers=AUTH, json={**VALID, "seed": 2})
            assert second.status_code == 202
            status_codes["queue_full"] = client.post(
                "/v1/images/generations", headers=AUTH, json={**VALID, "seed": 3}
            ).status_code
    finally:
        gate.set()

    unavailable = create_app(start_worker=False)
    with TestClient(unavailable) as client:
        status_codes["worker_unavailable"] = client.post(
            "/v1/images/generations", headers=AUTH, json=VALID
        ).status_code

    expected = {
        "missing_auth": 401,
        "invalid_auth": 403,
        "unknown_job": 404,
        "image_before_complete": 409,
        "blank_prompt": 422,
        "unsupported_1024": 422,
        "queue_full": 429,
        "worker_unavailable": 503,
    }
    assert status_codes == expected, status_codes
    record = {
        "source": "cpu_fastapi_contract_test",
        "scope": "coordinator_http_contract_without_gpu_inference",
        "status_codes": status_codes,
        "verdict": "PASS",
    }
    EVIDENCE.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))
    print("API_CONTRACT_ACCEPTANCE=PASS")


if __name__ == "__main__":
    main()
