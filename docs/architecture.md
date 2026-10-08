# Architecture

> 🌐 Language: **English** | [Tiếng Việt](architecture.vi.md)

## Design goal

Expose Z-Image-Turbo as a small production-style REST service on Kaggle T4×2 without pretending that two GPUs mean two independent replicas or 2× generation speed. The validated design keeps one logical BF16 pipeline resident across both GPUs and serializes generation.

## Process model

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
  | bounded admission + job state
  v
internal worker :8101
  |
  v
one resident ZImagePipeline
  |
  +-- transformer  -> cuda:0
  +-- text_encoder -> cuda:1
  +-- vae          -> cuda:1
```

The coordinator and worker both bind loopback. Only the coordinator may be tunneled. The worker is never intentionally exposed.

## GPU placement

The qualified map is:

- `transformer` → GPU0
- `text_encoder` → GPU1
- `vae` → GPU1

The pipeline is one logical model load spread across the two Tesla T4 devices. This is capacity distribution, not data-parallel throughput scaling.

## Scheduling

`JobManager` owns one background execution thread. Admission is guarded by a bounded semaphore representing one active generation plus the configured waiting capacity. The worker adds a non-blocking lock as a second single-flight guard.

This design intentionally rejects parallel GPU generation because the validated memory envelope is for one resident pipeline and one active inference trajectory.

## Fail-closed startup

Startup verifies:

1. CUDA is available.
2. At least two GPUs exist.
3. Both detected devices are Tesla T4.
4. The Kaggle model mount exists.
5. The model loads from local files only.
6. `hf_device_map` exactly matches the qualified placement.

No CPU fallback or network model download is used to hide a failed preflight.

## Runtime storage

Live PNGs are written to `outputs/`, per-request JSON to `metadata/`, and session state to `.runtime/`. These paths are ignored and are not release authority. Curated, sanitized evidence lives under `evidence/`.
