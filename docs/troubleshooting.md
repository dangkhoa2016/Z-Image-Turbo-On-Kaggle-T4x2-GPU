# Troubleshooting

> 🌐 Language: **English** | [Tiếng Việt](troubleshooting.vi.md)

## `/ready` returns 503

Check that the internal worker is running and inspect its sanitized log. Startup fails closed if the machine does not expose two Tesla T4 GPUs, the Kaggle model mount is missing, model loading fails, or the resulting device map differs from the qualified map.

## Authentication returns 401 or 403

401 means the Bearer header is missing. 403 means a token was supplied but does not match the current session token. Do not recover the value from Git history; generate/read only the current session-local token under `.runtime/`.

## Generation returns 429

The bounded queue is full. Wait for an admitted job to finish before submitting another request. Increasing queue size does not increase GPU execution concurrency.

## Image endpoint returns 409

The job exists but has not completed. Poll `GET /v1/jobs/{id}` until state becomes `complete`, then request the image.

## 768 fails after changing runtime dependencies

Treat this as a qualification regression. Do not silently lower checks or claim `high_768` remains supported. Reproduce on T4×2, collect memory/timing evidence, and update the supported surface only after a successful rerun.

## Tunnel URL stops working

Quick Tunnel endpoints are temporary. Restarting `cloudflared` or the Kaggle session can produce a different hostname. The repository deliberately does not persist the live URL.

## Notebook static verification fails

Run:

```bash
python scripts/verify_notebook_static.py notebooks/kaggle-t4x2-rest-server-production.ipynb
```

If payload hashes or expected files changed, investigate the source tree and notebook materialization logic rather than bypassing the verifier.
