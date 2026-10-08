# Đóng góp

> 🌐 Ngôn ngữ: [English](CONTRIBUTING.md) | **Tiếng Việt**

Cảm ơn bạn đã giúp cải thiện repository này.

## Trước khi gửi thay đổi

1. Đọc `README.vi.md`, `docs/architecture.vi.md`, `docs/qualification.vi.md` và `docs/limitations.vi.md`.
2. Giữ nguyên qualified contract: BF16, đúng hai Tesla T4, một logical pipeline resident, bounded single-flight generation và không CPU fallback.
3. Không commit API token, Quick Tunnel URL, Kaggle credential, PNG sinh ra, runtime log hoặc trạng thái `.runtime/`.
4. Giữ thay đổi tập trung và mô tả rõ ảnh hưởng đến qualification evidence.

## Kiểm tra phát triển

```bash
PYTHONPATH=src pytest -q
python -m compileall -q src scripts tests
for file in scripts/*.sh; do bash -n "$file"; done
python scripts/verify_notebook_static.py notebooks/kaggle-t4x2-rest-server-production.ipynb
```

Mọi tuyên bố live T4×2 cần evidence mới từ Kaggle. CI CPU/static hữu ích nhưng không thay thế live GPU qualification.

## Pull request

Dùng pull request template, giữ commit dễ review và thêm test/evidence cho thay đổi hành vi. Thay đổi tài liệu phải đồng bộ bản English và Tiếng Việt.
