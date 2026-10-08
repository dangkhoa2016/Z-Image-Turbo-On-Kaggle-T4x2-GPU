# Changelog

> 🌐 Language: **English** | [Tiếng Việt](CHANGELOG.vi.md)

All notable repository changes are documented here. Published releases follow semantic versioning.

## Unreleased

### Added

- Authenticated FastAPI coordinator with a loopback-only internal GPU worker.
- One resident BF16 `ZImagePipeline` spanning exactly two NVIDIA Tesla T4 GPUs.
- Bounded single-flight generation with one active request and a finite waiting queue.
- Qualified `safe_512` and `high_768` profiles with fail-closed validation.
- Golden, queue-endurance, mixed-profile, error-boundary, and public-path acceptance evidence.
- Reproducible production notebook and CPU/static GitHub Actions verification.
- English and Vietnamese documentation plus repository community/governance files.

### Qualification status

- Final qualification verdict: `PASS`.
- Golden 512 authority SHA-256: `56e0fca007d3da945de77788b5ab8a0a131b58730d93b624ca65e7c6ca6ea307`.
- Intentionally unsupported: FP16, 1024×1024, parallel GPU generation, CPU fallback, and pipeline-per-request reload.
