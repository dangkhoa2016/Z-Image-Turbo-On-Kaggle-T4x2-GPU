from __future__ import annotations

import json
import urllib.error
import urllib.request

WORKER_BASE = "http://127.0.0.1:8101"


def worker_ready() -> dict:
    try:
        with urllib.request.urlopen(WORKER_BASE + "/ready", timeout=5) as response:
            return json.load(response)
    except Exception as exc:
        return {"ready": False, "error": f"{type(exc).__name__}: {exc}"}


def run_generation(job: dict) -> dict:
    request = urllib.request.Request(
        WORKER_BASE + "/generate",
        data=json.dumps(job).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"worker HTTP {exc.code}: {body}") from exc
