# REST API

> 🌐 Ngôn ngữ: [English](api.md) | **Tiếng Việt**

Coordinator lắng nghe tại `127.0.0.1:8090`. Chỉ `/` và `/health` là public; mọi endpoint còn lại đều yêu cầu `Authorization: Bearer <token>`.

## Endpoint public

### `GET /`

Trả về metadata dịch vụ, loại API, version và các link discovery.

### `GET /health`

Trả về `{ "status": "ok" }` khi process coordinator còn sống. Đây là liveness check, không phải GPU readiness.

## Endpoint có authentication

### `GET /ready`

Chỉ trả HTTP 200 khi internal worker truy cập được và pipeline BF16 đã qualification đang sẵn sàng. Nếu không sẽ trả 503.

### `GET /v1/info`

Trả về service identifier, các profile đã qualification và trạng thái/runtime hiện tại của worker.

### `POST /v1/images/generations`

Request body:

```json
{
  "prompt": "A quiet coastal observatory under a star-filled sky",
  "seed": 42,
  "profile": "safe_512"
}
```

Profile được chấp nhận là `safe_512` và `high_768`. Khi admission thành công, API trả HTTP 202 cùng job id. GPU execution được serialize; khi bounded waiting queue đầy, admission trả HTTP 429.

### `GET /v1/jobs/{id}`

Trả trạng thái job: `queued`, `running`, `complete` hoặc `error`. Job hoàn tất có inference timing, SHA-256, image statistics, GPU memory telemetry, device map và metadata đường dẫn output.

### `GET /v1/jobs/{id}/image`

Trả PNG hoàn tất với media type `image/png`. Trả 409 khi job chưa hoàn thành.

## Error boundary

| Status | Ý nghĩa |
| ---: | --- |
| 401 | Thiếu Bearer token |
| 403 | Bearer token không hợp lệ |
| 404 | Không tìm thấy job hoặc output hoàn tất |
| 409 | Yêu cầu ảnh trước khi hoàn tất / worker busy guard |
| 422 | Prompt hoặc profile không hợp lệ |
| 429 | Bounded queue đầy |
| 503 | Worker không khả dụng hoặc chưa ready |

1024×1024 không phải API profile và bị từ chối trước GPU execution.

## Ghi chú bảo mật

API token được sinh cho từng live session và chỉ nên nằm trong `.runtime/`. Không nhúng token vào notebook, ví dụ, URL, log, screenshot hay file repository. Internal worker tại port `8101` là implementation detail và phải chỉ bind loopback.
