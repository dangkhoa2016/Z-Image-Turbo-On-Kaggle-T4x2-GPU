# Qualification Evidence

> 🌐 Language: **English** | [Tiếng Việt](qualification.vi.md)

This page summarizes accepted evidence from the live Kaggle T4×2 development and qualification session. Machine-readable records remain under `evidence/` and are the authority for exact values.

## Golden 512

- profile: `safe_512`
- seed: `42`
- BF16, 512×512, 9 steps, guidance 0.0
- worker inference: **52.483 s**
- SHA-256: `56e0fca007d3da945de77788b5ab8a0a131b58730d93b624ca65e7c6ca6ea307`
- unique colors: `90,846`
- verdict: **PASS**

## Five-job resident endurance

Five jobs were admitted almost simultaneously. Initial states were exactly one `running` plus four `queued`. All five completed sequentially with worker latencies:

`57.391 s`, `55.037 s`, `55.735 s`, `56.450 s`, `56.237 s`.

Allocated VRAM returned to the same post-warm-up baseline after each request. Queue serialization, resident-model endurance, and 512 memory stability passed.

## Mixed-profile sequence

Sequence: `safe_512 → high_768 → safe_512`.

Latencies: `59.134 s`, `127.837 s`, `56.352 s`.

Peak reserved memory during 768:

- GPU0: `15,378,415,616` bytes
- GPU1: `14,763,950,080` bytes

The post-768 512 request completed normally. Allocated memory plateaued; the larger reserved allocator cache stopped growing. Verdict: **PASS**.

## Error and security boundary

- missing auth → 401
- invalid auth → 403
- blank prompt → 422
- unsupported 1024 profile → 422
- worker remained ready afterwards

Verdict: **PASS**.

## Public REST path

A real `safe_512` request completed through Cloudflare HTTPS → coordinator → bounded queue → internal worker → PNG response. The Quick Tunnel hostname was intentionally scrubbed because it is ephemeral and not authority data. Verdict: **PASS**.

## Interpretation

The evidence supports an authenticated API-only service using BF16, one resident logical pipeline, bounded single-flight execution, `safe_512`, and `high_768`. It does **not** support claims of 2× inference speed, two independent replicas, FP16 support, 1024×1024 support, or parallel GPU generation.
