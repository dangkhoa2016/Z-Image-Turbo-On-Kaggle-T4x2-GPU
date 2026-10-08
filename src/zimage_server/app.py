import hmac
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator

from .config import DEFAULT_PROFILE, PROFILES
from .jobs import JobManager, QueueFullError


class GenerationRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4096)
    seed: int = 42
    profile: str = DEFAULT_PROFILE

    @field_validator("prompt")
    @classmethod
    def non_blank_prompt(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("prompt must not be blank")
        return value

    @field_validator("profile")
    @classmethod
    def known_profile(cls, value: str) -> str:
        if value not in PROFILES:
            raise ValueError("unknown profile")
        return value


def _auth(authorization: str | None = Header(default=None)) -> None:
    expected = os.environ.get("ZIMAGE_API_TOKEN", "")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    supplied = authorization[7:]
    if not expected or not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=403, detail="invalid bearer token")


def create_app(*, start_worker: bool = True, runner=None, readiness=None, max_queue_size: int = 4) -> FastAPI:
    if start_worker and runner is None:
        from .internal_client import run_generation, worker_ready
        runner = run_generation
        readiness = readiness or worker_ready

    manager = JobManager(runner=runner, max_queue_size=max_queue_size) if start_worker else None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        if manager is not None:
            manager.close()

    app = FastAPI(title="Z-Image-Turbo Kaggle T4x2 REST Server", version="0.1.0", lifespan=lifespan)

    @app.get("/", include_in_schema=False)
    def root_metadata():
        return {
            "service": "z-image-turbo-kaggle-t4x2",
            "type": "rest-api",
            "version": "0.1.0",
            "docs": "/docs",
            "health": "/health",
            "ready": "/ready",
            "info": "/v1/info",
        }

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/ready", dependencies=[Depends(_auth)])
    def ready():
        if manager is None:
            raise HTTPException(status_code=503, detail="worker not started")
        if readiness is None:
            return {"ready": True, "worker": "injected"}
        state = readiness()
        if not state.get("ready"):
            raise HTTPException(status_code=503, detail=state)
        return state

    @app.get("/v1/info", dependencies=[Depends(_auth)])
    def info():
        profiles = {name: vars(profile) for name, profile in PROFILES.items()}
        worker = readiness() if readiness is not None else {"ready": manager is not None}
        return {"service": "z-image-turbo-kaggle-t4x2", "profiles": profiles, "worker": worker}

    @app.post("/v1/images/generations", dependencies=[Depends(_auth)], status_code=202)
    def generate(request: GenerationRequest):
        if manager is None:
            raise HTTPException(status_code=503, detail="worker not ready")
        if readiness is not None and not readiness().get("ready"):
            raise HTTPException(status_code=503, detail="worker not ready")
        try:
            job_id = manager.submit(request.model_dump())
        except QueueFullError as exc:
            raise HTTPException(status_code=429, detail=str(exc)) from exc
        return {"id": job_id, "status": "queued", "profile": request.profile, "seed": request.seed}

    @app.get("/v1/jobs/{job_id}", dependencies=[Depends(_auth)])
    def job(job_id: str):
        if manager is None:
            raise HTTPException(status_code=503, detail="worker not ready")
        item = manager.get(job_id)
        if item is None:
            raise HTTPException(status_code=404, detail="job not found")
        return item

    @app.get("/v1/jobs/{job_id}/image", dependencies=[Depends(_auth)])
    def image(job_id: str):
        if manager is None:
            raise HTTPException(status_code=503, detail="worker not ready")
        item = manager.get(job_id)
        if item is None:
            raise HTTPException(status_code=404, detail="job not found")
        if item["status"] != "complete" or not item.get("result"):
            raise HTTPException(status_code=409, detail="job not complete")
        path = Path(item["result"].get("output_path", ""))
        if not path.is_file():
            raise HTTPException(status_code=404, detail="output missing")
        return FileResponse(path, media_type="image/png", filename=path.name)

    return app


app = create_app()
