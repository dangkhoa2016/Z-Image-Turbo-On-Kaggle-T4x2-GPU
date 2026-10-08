# Evidence qualification

> 🌐 Ngôn ngữ: [English](qualification.md) | **Tiếng Việt**

Trang này tóm tắt evidence đã được chấp nhận từ live session phát triển và qualification trên Kaggle T4×2. Các record machine-readable trong `evidence/` vẫn là authority cho giá trị chính xác.

## Golden 512

- profile: `safe_512`
- seed: `42`
- BF16, 512×512, 9 steps, guidance 0.0
- worker inference: **52.483 s**
- SHA-256: `56e0fca007d3da945de77788b5ab8a0a131b58730d93b624ca65e7c6ca6ea307`
- unique colors: `90,846`
- verdict: **PASS**

## Resident endurance 5 job

Năm job được admission gần như đồng thời. Trạng thái ban đầu chính xác là một `running` và bốn `queued`. Cả năm hoàn tất tuần tự với worker latency:

`57.391 s`, `55.037 s`, `55.735 s`, `56.450 s`, `56.237 s`.

Allocated VRAM trở về cùng post-warm-up baseline sau mỗi request. Queue serialization, resident-model endurance và memory stability ở 512 đều PASS.

## Mixed-profile sequence

Sequence: `safe_512 → high_768 → safe_512`.

Latency: `59.134 s`, `127.837 s`, `56.352 s`.

Peak reserved memory khi chạy 768:

- GPU0: `15,378,415,616` bytes
- GPU1: `14,763,950,080` bytes

Request 512 sau 768 vẫn hoàn tất bình thường. Allocated memory đạt plateau; phần reserved allocator cache lớn hơn ngừng tăng. Verdict: **PASS**.

## Error và security boundary

- thiếu auth → 401
- auth không hợp lệ → 403
- prompt rỗng → 422
- profile 1024 không hỗ trợ → 422
- worker vẫn ready sau đó

Verdict: **PASS**.

## Public REST path

Một request `safe_512` thực tế đã hoàn tất theo đường Cloudflare HTTPS → coordinator → bounded queue → internal worker → PNG response. Quick Tunnel hostname được chủ động scrub vì chỉ là endpoint tạm thời, không phải authority data. Verdict: **PASS**.

## Cách diễn giải

Evidence hỗ trợ một API-only service có authentication dùng BF16, một resident logical pipeline, bounded single-flight execution, `safe_512` và `high_768`. Evidence **không** hỗ trợ claim tốc độ inference gấp 2, hai replica độc lập, FP16, 1024×1024 hoặc parallel GPU generation.
