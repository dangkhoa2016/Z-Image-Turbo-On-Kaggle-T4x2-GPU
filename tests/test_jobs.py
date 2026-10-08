import threading
import time
import pytest
from zimage_server.jobs import JobManager, QueueFullError


def test_jobs_are_serialized_and_reach_complete():
    lock = threading.Lock()
    active = 0
    max_active = 0

    def runner(job):
        nonlocal active, max_active
        with lock:
            active += 1
            max_active = max(max_active, active)
        time.sleep(0.05)
        with lock:
            active -= 1
        return {"value": job["seed"]}

    mgr = JobManager(runner=runner, max_queue_size=3)
    try:
        ids = [mgr.submit({"seed": n}) for n in (1, 2, 3)]
        for jid in ids:
            assert mgr.wait(jid, timeout=2)["status"] == "complete"
        assert max_active == 1
    finally:
        mgr.close()


def test_queue_is_bounded():
    gate = threading.Event()

    def runner(job):
        gate.wait(1)
        return {}

    mgr = JobManager(runner=runner, max_queue_size=1)
    try:
        mgr.submit({"seed": 1})
        mgr.submit({"seed": 2})
        with pytest.raises(QueueFullError):
            mgr.submit({"seed": 3})
    finally:
        gate.set()
        mgr.close()
