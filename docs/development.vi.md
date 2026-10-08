# Hướng dẫn phát triển

> 🌐 Ngôn ngữ: [English](development.md) | **Tiếng Việt**

## Cấu trúc repository

- `src/zimage_server/` — coordinator, queue, validation, internal client và resident runtime.
- `scripts/` — server lifecycle cùng helper qualification/acceptance.
- `tests/` — CPU/static contract tests.
- `notebooks/` — production notebook Kaggle có thể tái lập.
- `evidence/` — qualification record machine-readable đã curate.
- `docs/` — tài liệu public song ngữ.

## Verification cục bộ

Lightweight test suite không cần model weights hay GPU:

```bash
PYTHONPATH=src pytest -q
python -m compileall -q src scripts tests
for file in scripts/*.sh; do bash -n "$file"; done
python scripts/verify_notebook_static.py notebooks/kaggle-t4x2-rest-server-production.ipynb
```

## Thay đổi runtime

Thay đổi device placement, dtype, model-loading behavior, profile size, step count, queue concurrency hoặc image validation đều làm thay đổi qualified contract. Những thay đổi đó cần fresh evidence trên Kaggle T4×2 trước khi cập nhật public support claim.

## Kỷ luật tài liệu

Mỗi tài liệu Markdown public được duy trì theo cặp English/Tiếng Việt với `.md` và `.vi.md`. Mỗi file mở đầu bằng language switch trực tiếp. Khi technical meaning thay đổi, cập nhật cả hai phía trong cùng change.

## Kỷ luật commit

Giữ code commit tập trung và dễ review. Tránh gộp implementation, evidence, governance và tài liệu dài vào một giant diff. Tài liệu release-facing nên được hoàn thiện sau khi implementation và verification surface đã ổn định.
