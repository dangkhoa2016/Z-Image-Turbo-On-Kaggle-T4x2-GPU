from __future__ import annotations

import os
import threading
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .runtime import ZImageRuntime

_runtime = ZImageRuntime()
_state = {"status": "starting", "error": None, "load": None}
_lock = threading.Lock()


class WorkerRequest(BaseModel):
    prompt: str
    seed: int
    profile: str
    request_id: str | None = None


def _load_runtime():
    try:
        _state["status"] = "loading_model"
        _state["load"] = _runtime.load()
        _state["status"] = "ready"
    except Exception as exc:
        _state["status"] = "error"
        _state["error"] = {"type": type(exc).__name__, "message": str(exc)}


@asynccontextmanager
async def lifespan(app: FastAPI):
    _load_runtime()
    yield


app = FastAPI(title="Z-Image-Turbo Internal Worker", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": _state["status"]}


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
