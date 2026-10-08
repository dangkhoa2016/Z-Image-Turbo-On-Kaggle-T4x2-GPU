# Kaggle Runtime

> 🌐 Language: **English** | [Tiếng Việt](kaggle-runtime.vi.md)

## Qualified environment

| Component | Qualified value |
| --- | --- |
| GPU | 2 × NVIDIA Tesla T4 |
| Python | 3.13.15 |
| PyTorch | 2.11.0+cu128 |
| CUDA runtime | 12.8 |
| diffusers | 0.40.0 |
| transformers | 5.16.1 |
| accelerate | 1.14.0 |
| dtype | BF16 |

Attached Kaggle model:

`/kaggle/input/models/dangkhoa2016/tongyi-mai-z-image-turbo/pytorch/default/1`

The server loads directly from Kaggle Input with `local_files_only=True`. Do not stage the full model into `/tmp`; the qualified direct-load path is simpler and avoids unnecessary disk duplication.

## Startup sequence

1. Attach `dangkhoa2016/tongyi-mai-z-image-turbo/PyTorch/default/1` to the notebook.
2. Confirm exactly two Tesla T4 GPUs.
3. Materialize the repository source or use the production notebook payload.
4. Generate a per-session API token under `.runtime/api_token` with restricted permissions.
5. Start the internal worker on `127.0.0.1:8101`.
6. Wait until the worker reports the BF16 pipeline and expected device map.
7. Start the coordinator on `127.0.0.1:8090`.
8. Run local health/readiness and REST acceptance checks.
9. Optionally start a Cloudflare Quick Tunnel targeting only port `8090`.

## Qualified profiles

| Profile | Size | Steps | Guidance | Qualification |
| --- | ---: | ---: | ---: | --- |
| `safe_512` | 512×512 | 9 | 0.0 | default, qualified |
| `high_768` | 768×768 | 9 | 0.0 | qualified single-flight; close to T4 memory ceiling |

Do not expose 1024×1024. Do not use FP16 as an automatic fallback.

## Session-local files

`.runtime/` may contain the API token, process ids, tunnel URL, and downloaded `cloudflared` binary. `outputs/`, `metadata/`, and logs are also transient. None of these belong in Git history or release archives.
