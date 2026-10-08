# Limitations

> 🌐 Language: **English** | [Tiếng Việt](limitations.vi.md)

The project intentionally publishes its validated boundary instead of silently widening support.

## Unsupported precision

FP16 is not a fallback. During qualification, the tested FP16 path produced a degenerate all-black result, so the public contract remains BF16 only.

## Unsupported resolution

1024×1024 is not exposed as a profile. Prior qualification reached GPU out-of-memory, therefore the coordinator rejects unsupported profile requests before GPU execution.

## No parallel generation

The two T4 GPUs host different components of one logical pipeline. They are not separate model replicas. GPU generation remains single-flight even when several REST requests are waiting.

## 768 memory margin

`high_768` passed mixed-profile qualification but operates close to the Tesla T4 memory ceiling. It is qualified for single-flight use, not as evidence that arbitrary larger dimensions are safe.

## Ephemeral networking

Cloudflare Quick Tunnel is useful for acceptance testing but is not a durable production endpoint. Its generated hostname can change between sessions and is deliberately excluded from authority artifacts.

## Kaggle lifecycle

Kaggle sessions are ephemeral. The service, token, tunnel, generated images, logs, and in-memory model disappear with the session unless the user explicitly saves permitted artifacts.

## Scope of CI

GitHub Actions validates source contracts, tests, shell syntax, notebook structure, and repository hygiene without a T4×2 runtime. A green CPU/static CI run is not a substitute for fresh live GPU evidence when runtime behavior changes.
