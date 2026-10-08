# Contributing

> 🌐 Language: **English** | [Tiếng Việt](CONTRIBUTING.vi.md)

Thanks for helping improve this repository.

## Before opening a change

1. Read `README.md`, `docs/architecture.md`, `docs/qualification.md`, and `docs/limitations.md`.
2. Preserve the qualified contract: BF16, exactly two Tesla T4 GPUs, one resident logical pipeline, bounded single-flight generation, and no CPU fallback.
3. Never commit API tokens, Quick Tunnel URLs, Kaggle credentials, generated PNGs, runtime logs, or `.runtime/` state.
4. Keep changes focused and explain any effect on qualification evidence.

## Development checks

```bash
PYTHONPATH=src pytest -q
python -m compileall -q src scripts tests
for file in scripts/*.sh; do bash -n "$file"; done
python scripts/verify_notebook_static.py notebooks/kaggle-t4x2-rest-server-production.ipynb
```

Live T4×2 claims require fresh Kaggle evidence. CPU/static CI is useful, but it never substitutes for live GPU qualification.

## Pull requests

Use the pull request template, keep commits reviewable, and include tests or evidence for behavior changes. Documentation changes must keep English and Vietnamese counterparts synchronized.
