# Z-Image-Turbo on Kaggle T4×2 GPU

<p align="center">
  <a href="https://github.com/dangkhoa2016/Z-Image-Turbo-On-Kaggle-T4x2-GPU/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/dangkhoa2016/Z-Image-Turbo-On-Kaggle-T4x2-GPU/actions/workflows/ci.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/License-MIT-green.svg"></a>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white">
  <img alt="GPU" src="https://img.shields.io/badge/GPU-Tesla%20T4%20%C3%972-76B900?logo=nvidia&logoColor=white">
  <img alt="Precision" src="https://img.shields.io/badge/Precision-BF16-2563EB">
  <img alt="API" src="https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white">
  <img alt="Queue" src="https://img.shields.io/badge/GPU%20Execution-Single--flight-7C3AED">
  <img alt="Qualification" src="https://img.shields.io/badge/Qualification-PASS-0A7E07">
  <img alt="Kaggle" src="https://img.shields.io/badge/Kaggle-T4%20%C3%972-20BEFF?logo=kaggle&logoColor=white">
</p>

> 🌐 Language: **English** | [Tiếng Việt](README.vi.md)

A reproducible engineering project for running **Tongyi-MAI/Z-Image-Turbo** as an authenticated, API-only image-generation service on **Kaggle NVIDIA Tesla T4 ×2**.

The qualified design keeps **one BF16 `ZImagePipeline` resident across both GPUs**, serializes GPU generation through a bounded queue, exposes a FastAPI coordinator, records deterministic acceptance evidence, and can optionally expose only the coordinator through a temporary Cloudflare Quick Tunnel.

This is an independent engineering project around the upstream Z-Image-Turbo model. It is not an official Tongyi-MAI release.

---

## At a glance

| Area | Qualified public contract |
| --- | --- |
| Model source | Kaggle mirror of `Tongyi-MAI/Z-Image-Turbo` |
| Accelerator | Exactly **2 × NVIDIA Tesla T4** |
| Precision | **BF16** |
| Logical model loads | **1 resident pipeline** |
| Transformer | `cuda:0` |
| Text encoder | `cuda:1` |
| VAE | `cuda:1` |
| API | FastAPI coordinator on `127.0.0.1:8090` |
| Internal worker | Loopback-only on `127.0.0.1:8101` |
| GPU scheduling | **Single-flight**, bounded waiting queue |
| Default profile | `safe_512` — 512×512, 9 steps, guidance 0.0 |
| Larger profile | `high_768` — 768×768, 9 steps, guidance 0.0 |
| Golden 512 | **52.483 s**, SHA-256 authority preserved |
| Qualification | **PASS** |
| License | MIT for this repository's original code/docs |

The two T4 GPUs provide capacity for **one logical pipeline**. This repository does **not** claim 2× inference speed or two independent serving replicas.

---

## Why this project exists

A model that fits and generates one image is not yet a production-style serving example. This repository focuses on the engineering boundary around a reproducible Kaggle REST service:

- keep the model hot instead of reloading it per request;
- distribute one logical pipeline across both T4 GPUs;
- require explicit Bearer authentication for generation and job data;
- separate the public coordinator from the internal GPU worker;
- serialize GPU execution to stay within the validated memory envelope;
- bound queue admission instead of allowing unbounded waiting work;
- reject unsupported profiles before GPU execution;
- preserve timings, memory telemetry, hashes, and acceptance evidence;
- keep runtime credentials and ephemeral tunnel information out of Git history.

The goal is not only to generate an image. The goal is to make the serving path **inspectable, reproducible, and honest about its limits**.

---

## Architecture

```text
client
  |
  | optional HTTPS
  v
Cloudflare Quick Tunnel
  |
  v
FastAPI coordinator :8090
  |
  | auth + validation + bounded admission + job state
  v
internal worker :8101
  |
  v
one resident BF16 ZImagePipeline
  |
  +-- transformer  -> cuda:0
  +-- text_encoder -> cuda:1
  +-- VAE          -> cuda:1
```

Only the coordinator may be tunneled. The worker remains loopback-only. See [Architecture](docs/architecture.md) for the complete process, scheduling, placement, and fail-closed design.

---

## REST surface

Public:

- `GET /` — service metadata;
- `GET /health` — coordinator liveness.

Bearer-authenticated:

- `GET /ready` — worker and runtime readiness;
- `GET /v1/info` — profiles and runtime identity;
- `POST /v1/images/generations` — submit a generation job;
- `GET /v1/jobs/{id}` — poll job state and result metadata;
- `GET /v1/jobs/{id}/image` — fetch the completed PNG.

Example request body:

```json
{
  "prompt": "A quiet coastal observatory under a star-filled sky",
  "seed": 42,
  "profile": "safe_512"
}
```

See [REST API](docs/api.md) for authentication and status-code contracts.

---

## Qualified profiles

| Profile | Resolution | Steps | Guidance | Status |
| --- | ---: | ---: | ---: | --- |
| `safe_512` | 512×512 | 9 | 0.0 | Qualified default |
| `high_768` | 768×768 | 9 | 0.0 | Qualified single-flight; near T4 memory ceiling |

1024×1024 is intentionally rejected before GPU execution. FP16 is intentionally not used as a fallback because the validated FP16 experiment produced a degenerate all-black output.

---

## Qualification highlights

### Golden 512

`safe_512`, seed 42:

- worker inference: **52.483 s**;
- SHA-256: `56e0fca007d3da945de77788b5ab8a0a131b58730d93b624ca65e7c6ca6ea307`;
- unique colors: `90,846`;
- verdict: **PASS**.

### Five-job resident endurance

Five nearly simultaneous submissions entered the system as exactly **one `running` + four `queued`**. All five completed sequentially with worker latencies of `57.391`, `55.037`, `55.735`, `56.450`, and `56.237` seconds.

### Mixed profile

`512 → 768 → 512` completed in `59.134`, `127.837`, and `56.352` seconds. The final 512 request completed normally after the higher-memory 768 request. Verdict: **PASS**.

### Error/security boundary

Missing auth → 401, invalid auth → 403, blank prompt → 422, unsupported 1024 profile → 422, with the worker remaining ready afterwards.

Full details: [Qualification Evidence](docs/qualification.md) and [`evidence/qualification-summary.json`](evidence/qualification-summary.json).

---

## Reproducible Kaggle workflow

The qualified model is attached as:

`dangkhoa2016/tongyi-mai-z-image-turbo/PyTorch/default/1`

and loaded directly from:

`/kaggle/input/models/dangkhoa2016/tongyi-mai-z-image-turbo/pytorch/default/1`

with `local_files_only=True`.

The production notebook is:

[`notebooks/kaggle-t4x2-rest-server-production.ipynb`](notebooks/kaggle-t4x2-rest-server-production.ipynb)

The current accepted notebook identity and reproducibility rules are documented in [Reproducibility and Evidence](docs/reproducibility.md).

---

## Local verification

The lightweight repository gates do not require GPU model weights:

```bash
PYTHONPATH=src pytest -q
python -m compileall -q src scripts tests
for file in scripts/*.sh; do bash -n "$file"; done
python scripts/verify_notebook_static.py notebooks/kaggle-t4x2-rest-server-production.ipynb
```

Live runtime claims still require fresh Kaggle T4×2 evidence when the qualified contract changes.

---

## Documentation

| Topic | English | Tiếng Việt |
| --- | --- | --- |
| REST API | [docs/api.md](docs/api.md) | [docs/api.vi.md](docs/api.vi.md) |
| Architecture | [docs/architecture.md](docs/architecture.md) | [docs/architecture.vi.md](docs/architecture.vi.md) |
| Kaggle runtime | [docs/kaggle-runtime.md](docs/kaggle-runtime.md) | [docs/kaggle-runtime.vi.md](docs/kaggle-runtime.vi.md) |
| Qualification | [docs/qualification.md](docs/qualification.md) | [docs/qualification.vi.md](docs/qualification.vi.md) |
| Limitations | [docs/limitations.md](docs/limitations.md) | [docs/limitations.vi.md](docs/limitations.vi.md) |
| Development | [docs/development.md](docs/development.md) | [docs/development.vi.md](docs/development.vi.md) |
| Troubleshooting | [docs/troubleshooting.md](docs/troubleshooting.md) | [docs/troubleshooting.vi.md](docs/troubleshooting.vi.md) |
| Reproducibility | [docs/reproducibility.md](docs/reproducibility.md) | [docs/reproducibility.vi.md](docs/reproducibility.vi.md) |
| Changelog | [CHANGELOG.md](CHANGELOG.md) | [CHANGELOG.vi.md](CHANGELOG.vi.md) |

Repository governance under `.github/` is also maintained in English/Vietnamese pairs where GitHub supports paired human-readable files/templates.

---

## Intentionally unsupported

- FP16 serving fallback;
- 1024×1024 generation;
- concurrent GPU generation;
- two independent resident model replicas;
- pipeline-per-request model reload;
- CPU inference fallback;
- runtime Hugging Face download fallback;
- staging the complete model into `/tmp`;
- HTML/Gradio inference UI;
- treating a Quick Tunnel hostname as a stable deployment URL.

See [Limitations](docs/limitations.md) before changing these boundaries.

---

## Security

The API token is generated per session and must never be committed, embedded in public URLs, or copied into evidence. The internal worker is loopback-only. Quick Tunnel URLs are ephemeral and excluded from release authority.

See [Security Policy](.github/SECURITY.md) for reporting and project-specific boundaries.

---

## License

This repository's original code and documentation are licensed under the [MIT License](LICENSE):

**Copyright (c) 2026 Đăng Khoa <i.am@dangkhoa.dev>**

Model weights are not redistributed by this repository and remain subject to their upstream/model-host licensing terms.
