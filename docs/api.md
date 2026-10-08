# REST API

> 🌐 Language: **English** | [Tiếng Việt](api.vi.md)

The coordinator listens on `127.0.0.1:8090`. Only `/` and `/health` are public; every other endpoint requires `Authorization: Bearer <token>`.

## Public endpoints

### `GET /`

Returns service metadata, API type, version, and discovery links.

### `GET /health`

Returns `{ "status": "ok" }` when the coordinator process is alive. This is a liveness check, not GPU readiness.

## Authenticated endpoints

### `GET /ready`

Returns HTTP 200 only when the internal worker is reachable and its qualified BF16 pipeline is ready. Returns 503 otherwise.

### `GET /v1/info`

Returns the service identifier, qualified profiles, and current worker readiness/runtime information.

### `POST /v1/images/generations`

Request body:

```json
{
  "prompt": "A quiet coastal observatory under a star-filled sky",
  "seed": 42,
  "profile": "safe_512"
}
```

Accepted profiles are `safe_512` and `high_768`. Successful admission returns HTTP 202 with a job id. GPU execution is serialized; when the bounded waiting queue is full, admission returns HTTP 429.

### `GET /v1/jobs/{id}`

Returns job state: `queued`, `running`, `complete`, or `error`. Completed jobs include inference timing, SHA-256, image statistics, GPU memory telemetry, device map, and output path metadata.

### `GET /v1/jobs/{id}/image`

Returns the completed PNG as `image/png`. Returns 409 while the job is incomplete.

## Error boundary

| Status | Meaning |
| ---: | --- |
| 401 | Bearer token missing |
| 403 | Bearer token invalid |
| 404 | Job or completed output not found |
| 409 | Image requested before completion / worker busy guard |
| 422 | Invalid prompt or profile |
| 429 | Bounded queue full |
| 503 | Worker unavailable or not ready |

1024×1024 is not an API profile and is rejected before GPU execution.

## Security notes

The API token is generated per live session and belongs under `.runtime/`. Do not embed it in notebooks, examples, URLs, logs, screenshots, or repository files. The internal worker on port `8101` is implementation detail and must remain loopback-only.
