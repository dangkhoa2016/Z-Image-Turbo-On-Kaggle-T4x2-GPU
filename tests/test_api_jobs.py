import os
import time
os.environ.setdefault("ZIMAGE_API_TOKEN", "test-token-abcdefghijklmnopqrstuvwxyz-123456")
from fastapi.testclient import TestClient
from zimage_server.app import create_app

H = {"Authorization": "Bearer test-token-abcdefghijklmnopqrstuvwxyz-123456"}


def test_submit_and_poll_job():
    def runner(job):
        return {"sha256": "abc123", "image_path": "/tmp/fake.png", "inference_seconds": 0.01}

    app = create_app(start_worker=True, runner=runner, max_queue_size=2)
    with TestClient(app) as client:
        r = client.post("/v1/images/generations", headers=H, json={"prompt": "hello", "seed": 42, "profile": "safe_512"})
        assert r.status_code == 202
        body = r.json()
        assert body["status"] == "queued"
        assert body["id"]
        for _ in range(50):
            j = client.get("/v1/jobs/" + body["id"], headers=H)
            assert j.status_code == 200
            if j.json()["status"] == "complete":
                break
            time.sleep(0.02)
        assert j.json()["status"] == "complete"
        assert j.json()["result"]["sha256"] == "abc123"
