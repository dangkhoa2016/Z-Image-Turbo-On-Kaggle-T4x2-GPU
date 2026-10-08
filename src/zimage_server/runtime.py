from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import torch
from diffusers import ZImagePipeline

from .config import PROFILES
from .validation import validate_image

MODEL_PATH = Path("/kaggle/input/models/dangkhoa2016/tongyi-mai-z-image-turbo/pytorch/default/1")
OUTPUT_ROOT = Path("/kaggle/working/Z-Image-Turbo-Kaggle-T4x2-REST-Server/outputs")
METADATA_ROOT = Path("/kaggle/working/Z-Image-Turbo-Kaggle-T4x2-REST-Server/metadata")
EXPECTED_DEVICE_MAP = {"transformer": 0, "text_encoder": 1, "vae": 1}


class ZImageRuntime:
    def __init__(self):
        self.pipe = None
        self.load_seconds = None
        self.device_map = None

    def preflight(self) -> dict:
        if not torch.cuda.is_available() or torch.cuda.device_count() < 2:
            raise RuntimeError("GPU_T4X2_REQUIRED")
        names = [torch.cuda.get_device_name(i) for i in range(2)]
        if any("T4" not in name for name in names):
            raise RuntimeError(f"GPU_T4X2_REQUIRED: {names}")
        if not MODEL_PATH.is_dir() or not (MODEL_PATH / "model_index.json").is_file():
            raise RuntimeError("MODEL_INPUT_MISSING")
        return {"gpu_names": names, "model_path": str(MODEL_PATH), "dtype": "bfloat16"}

    def load(self) -> dict:
        preflight = self.preflight()
        started = time.perf_counter()
        self.pipe = ZImagePipeline.from_pretrained(
            str(MODEL_PATH),
            dtype=torch.bfloat16,
            device_map="balanced",
            max_memory={0: "14GiB", 1: "14GiB", "cpu": "28GiB"},
            local_files_only=True,
        )
        self.load_seconds = time.perf_counter() - started
        self.device_map = dict(self.pipe.hf_device_map)
        if self.device_map != EXPECTED_DEVICE_MAP:
            raise RuntimeError(f"UNEXPECTED_DEVICE_MAP: {self.device_map}")
        return {**preflight, "model_load_seconds": self.load_seconds, "device_map": self.device_map}

    def generate(self, job: dict) -> dict:
        if self.pipe is None:
            raise RuntimeError("MODEL_NOT_LOADED")
        profile = PROFILES[job["profile"]]
        request_id = job["request_id"]
        for i in range(2):
            torch.cuda.reset_peak_memory_stats(i)
        before = self._memory()
        generator = torch.Generator(device="cuda:0").manual_seed(int(job["seed"]))
        started = time.perf_counter()
        image = self.pipe(
            prompt=job["prompt"],
            height=profile.height,
            width=profile.width,
            num_inference_steps=profile.steps,
            guidance_scale=profile.guidance_scale,
            generator=generator,
        ).images[0]
        inference_seconds = time.perf_counter() - started
        stats = validate_image(image, profile.width, profile.height)
        OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
        METADATA_ROOT.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_ROOT / f"{request_id}.png"
        image.save(output_path, format="PNG")
        digest = hashlib.sha256(output_path.read_bytes()).hexdigest()
        after = self._memory()
        result = {
            "request_id": request_id,
            "profile": job["profile"],
            "seed": int(job["seed"]),
            "width": profile.width,
            "height": profile.height,
            "steps": profile.steps,
            "guidance_scale": profile.guidance_scale,
            "dtype": "bfloat16",
            "inference_seconds": inference_seconds,
            "sha256": digest,
            "output_path": str(output_path),
            "pixel_stats": stats,
            "memory_before": before,
            "memory_after": after,
            "device_map": self.device_map,
        }
        (METADATA_ROOT / f"{request_id}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        return result

    @staticmethod
    def _memory() -> dict:
        return {
            f"gpu{i}": {
                "allocated": int(torch.cuda.memory_allocated(i)),
                "reserved": int(torch.cuda.memory_reserved(i)),
                "peak_allocated": int(torch.cuda.max_memory_allocated(i)),
                "peak_reserved": int(torch.cuda.max_memory_reserved(i)),
            }
            for i in range(2)
        }
