# Nhật ký thay đổi

> 🌐 Ngôn ngữ: [English](CHANGELOG.md) | **Tiếng Việt**

Các thay đổi đáng chú ý của repository được ghi lại tại đây. Các bản phát hành công khai tuân theo semantic versioning.

## Chưa phát hành

### Đã bổ sung

- FastAPI coordinator có authentication và GPU worker nội bộ chỉ bind loopback.
- Một `ZImagePipeline` BF16 resident trải trên đúng hai GPU NVIDIA Tesla T4.
- Bounded single-flight generation với một request đang chạy và hàng đợi hữu hạn.
- Hai profile đã qualification là `safe_512` và `high_768`, kèm fail-closed validation.
- Evidence cho golden, queue endurance, mixed profile, error boundary và public REST path.
- Production notebook có thể tái lập cùng GitHub Actions cho các kiểm tra CPU/static.
- Bộ tài liệu và governance song ngữ English/Tiếng Việt.

### Trạng thái qualification

- Final qualification verdict: `PASS`.
- Golden 512 authority SHA-256: `56e0fca007d3da945de77788b5ab8a0a131b58730d93b624ca65e7c6ca6ea307`.
- Chủ động không hỗ trợ: FP16, 1024×1024, parallel GPU generation, CPU fallback và pipeline-per-request reload.
