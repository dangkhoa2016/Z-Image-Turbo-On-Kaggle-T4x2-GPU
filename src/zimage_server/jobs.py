from __future__ import annotations

import queue
import threading
import time
import uuid
from copy import deepcopy
from typing import Callable


class QueueFullError(RuntimeError):
    pass


class JobManager:
    def __init__(self, runner: Callable[[dict], dict], max_queue_size: int = 4):
        self._runner = runner
        self._queue: queue.Queue[tuple[str, dict] | None] = queue.Queue()
        self._admission = threading.BoundedSemaphore(max_queue_size + 1)
        self._jobs: dict[str, dict] = {}
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._loop, name="zimage-job-worker", daemon=True)
        self._thread.start()

    def submit(self, payload: dict) -> str:
        job_id = "img_" + uuid.uuid4().hex
        now = time.time()
        record = {"id": job_id, "status": "queued", "submitted_at": now, "payload": deepcopy(payload), "result": None, "error": None}
        with self._lock:
            self._jobs[job_id] = record
        if not self._admission.acquire(blocking=False):
            with self._lock:
                self._jobs.pop(job_id, None)
            raise QueueFullError("request queue is full")
        self._queue.put_nowait((job_id, deepcopy(payload)))
        return job_id

    def get(self, job_id: str) -> dict | None:
        with self._lock:
            item = self._jobs.get(job_id)
            return deepcopy(item) if item else None

    def wait(self, job_id: str, timeout: float) -> dict:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            item = self.get(job_id)
            if item is None:
                raise KeyError(job_id)
            if item["status"] in {"complete", "error"}:
                return item
            time.sleep(0.01)
        raise TimeoutError(job_id)

    def close(self) -> None:
        try:
            self._queue.put_nowait(None)
        except queue.Full:
            pass
        self._thread.join(timeout=2)

    def _loop(self) -> None:
        while True:
            item = self._queue.get()
            if item is None:
                self._queue.task_done()
                return
            job_id, payload = item
            payload = dict(payload)
            payload["request_id"] = job_id
            try:
                with self._lock:
                    self._jobs[job_id]["status"] = "running"
                    self._jobs[job_id]["started_at"] = time.time()
                result = self._runner(payload)
                with self._lock:
                    self._jobs[job_id]["status"] = "complete"
                    self._jobs[job_id]["finished_at"] = time.time()
                    self._jobs[job_id]["result"] = result
            except Exception as exc:
                with self._lock:
                    self._jobs[job_id]["status"] = "error"
                    self._jobs[job_id]["finished_at"] = time.time()
                    self._jobs[job_id]["error"] = {"type": type(exc).__name__, "message": str(exc)}
            finally:
                self._admission.release()
                self._queue.task_done()
