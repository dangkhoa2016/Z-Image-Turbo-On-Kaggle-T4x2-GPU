from __future__ import annotations

import os
import threading
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .runtime import ZImageRuntime

_runtime = ZImageRuntime()
_state = {"status": "starting", "error": None, "load": None, "started_at": None, "finished_at": None}
_lock = threading.Lock()


class WorkerRequest(BaseModel):
    prompt: str
    seed: int
    profile: str
    request_id: str | None = None


def _load_runtime():
    _state.update(status="loading_model", error=None, load=None, started_at=time.time(), finished_at=None)
    try:
        _state["load"] = _runtime.load()
        _state["status"] = "ready"
    except Exception as exc:
        _state["status"] = "error"
        _state["error"] = {"type": type(exc).__name__, "message": str(exc)}
    finally:
        _state["finished_at"] = time.time()


def _start_runtime_load():
    thread = threading.Thread(target=_load_runtime, name="zimage-model-loader", daemon=True)
    thread.start()
    return thread


@asynccontextmanager
async def lifespan(app: FastAPI):
    _start_runtime_load()
    yield


app = FastAPI(title="Z-Image-Turbo Internal Worker", lifespan=lifespan)


@app.get("/health")
def health():
    started = _state.get("started_at")
    finished = _state.get("finished_at")
    elapsed = None
    if started is not None:
        elapsed = max(0.0, (finished or time.time()) - started)
    return {
        "status": _state["status"],
        "elapsed_seconds": elapsed,
        "error": _state.get("error"),
    }


@app.get("/ready")
def ready():
    if _state["status"] != "ready":
        raise HTTPException(status_code=503, detail=_state)
    return {"ready": True, "load": _state["load"]}


@app.post("/generate")
def generate(req: WorkerRequest):
    if _state["status"] != "ready":
        raise HTTPException(status_code=503, detail=_state)
    if not _lock.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="worker busy")
    try:
        payload = req.model_dump()
        payload["request_id"] = payload["request_id"] or ("img_" + uuid.uuid4().hex)
        return _runtime.generate(payload)
    finally:
        _lock.release()
