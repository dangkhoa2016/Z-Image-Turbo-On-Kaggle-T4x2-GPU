# Changelog

> 🌐 Language: **English** | [Tiếng Việt](CHANGELOG.vi.md)

All notable repository changes are documented here. Published releases follow semantic versioning.

## v1.0.0 — 2026-10-09

### Added

- Authenticated FastAPI coordinator with a loopback-only internal GPU worker.
- One resident BF16 `ZImagePipeline` spanning exactly two NVIDIA Tesla T4 GPUs.
- Bounded single-flight generation with one active request and a finite waiting queue.
- Qualified `safe_512` and `high_768` profiles with fail-closed validation.
- Golden, queue-endurance, mixed-profile, error-boundary, and public-path acceptance evidence.
- Reproducible production notebook and CPU/static GitHub Actions verification.
- English and Vietnamese documentation plus repository community/governance files.
- Explicit third-party model licensing and attribution for `Tongyi-MAI/Z-Image-Turbo`, pinned to upstream revision `f332072aa78be7aecdf3ee76d5c247082da564a6` and documented as Apache License 2.0.
- Repository-level `THIRD_PARTY_NOTICES.md` plus a local reference copy of Apache License 2.0.

### Qualification status

- Final qualification verdict: `PASS`.
- Official Kaggle Saved Version acceptance: `PASS` on the optimized parallel-loading candidate.
- Official executed notebook SHA-256: `488f881fbcd006e40de529d1e8c27a76f869a5370b0c97e4fcc3f3d041976599`.
- Official model load: `124.084353364` seconds with four Hugging Face parallel-loading workers.
- Golden 512 authority SHA-256: `56e0fca007d3da945de77788b5ab8a0a131b58730d93b624ca65e7c6ca6ea307`.
- Intentionally unsupported: FP16, 1024×1024, parallel GPU generation, CPU fallback, and pipeline-per-request reload.
