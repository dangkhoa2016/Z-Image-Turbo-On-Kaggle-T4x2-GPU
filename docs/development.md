# Development Guide

> 🌐 Language: **English** | [Tiếng Việt](development.vi.md)

## Repository layout

- `src/zimage_server/` — coordinator, queue, validation, internal client, and resident runtime.
- `scripts/` — server lifecycle and qualification/acceptance helpers.
- `tests/` — CPU/static contract tests.
- `notebooks/` — reproducible Kaggle production notebook.
- `evidence/` — curated machine-readable qualification records.
- `docs/` — bilingual public documentation.

## Local verification

The lightweight test suite does not require model weights or a GPU:

```bash
PYTHONPATH=src pytest -q
python -m compileall -q src scripts tests
for file in scripts/*.sh; do bash -n "$file"; done
python scripts/verify_notebook_static.py notebooks/kaggle-t4x2-rest-server-production.ipynb
```

## Runtime changes

Changes to device placement, dtype, model-loading behavior, profile sizes, step counts, queue concurrency, or image validation alter the qualified contract. Such changes require fresh Kaggle T4×2 evidence before public support claims are updated.

## Documentation discipline

Every public Markdown document is maintained as an English/Vietnamese pair using `.md` and `.vi.md`. Each file begins with a direct language switch. Update both sides in the same change whenever technical meaning changes.

## Commit discipline

Keep code commits focused and reviewable. Avoid combining implementation, evidence, governance, and long documentation into one giant diff. Release-facing documentation should be finalized after the implementation and verification surface has stabilized.
