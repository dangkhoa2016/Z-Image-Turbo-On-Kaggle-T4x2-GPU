# Reproducibility and Evidence

> 🌐 Language: **English** | [Tiếng Việt](reproducibility.vi.md)

## What is authority

The release-facing runtime claims are grounded in:

- the exact source tree;
- the production notebook;
- curated records under `evidence/`;
- the pinned Kaggle model variation/version;
- the qualified software and hardware environment.

Pretty screenshots or a temporary tunnel URL are not authority.

## Production notebook identity

The current repository candidate is `notebooks/kaggle-t4x2-rest-server-production.ipynb`. Its bilingual Step workflow keeps the audited 30-file embedded payload unchanged while enabling the qualified Hugging Face parallel-loading launch environment before Diffusers is imported.

Current candidate Git blob:

`64f4b40b7dcb65b8f258505931d7ecf40c615402`

Current candidate SHA-256:

`1aeaefb88b325ac068f996e7f1e6aaaf5f6e73e1fcf5b6de363d3426bd129d33`

Embedded payload SHA-256 remains `3297e31dc53177e547d09b3d33febc2ebb46aba305398272dc9899d6528e3cfe`; manifest SHA-256 remains `5fbc29b146223409db3f97dc6619a6e68df78a386a4cd3c5689406c4e44bcb66` with 30 files.

The release acceptance run is a fresh Kaggle Saved Version executed from the current optimized source candidate (SHA-256 `1aeaefb88b325ac068f996e7f1e6aaaf5f6e73e1fcf5b6de363d3426bd129d33`) on the project owner's official Kaggle account. The downloaded executed notebook artifact has SHA-256 `488f881fbcd006e40de529d1e8c27a76f869a5370b0c97e4fcc3f3d041976599`: all 11 code cells executed, there were zero error outputs, nine PNG outputs were embedded, and the run ended with `FINAL_QUALIFICATION=PASS` and `EVIDENCE_VERIFY=PASS`.

The same run confirmed `HF_ENABLE_PARALLEL_LOADING=YES` with four workers, a model-load time of `124.084353364` seconds, the qualified BF16 device map, exact golden SHA-256 `56e0fca007d3da945de77788b5ab8a0a131b58730d93b624ca65e7c6ca6ea307`, five-job queue endurance, live error boundaries, and mixed `512→768→512` qualification. The optional public Quick Tunnel gate was intentionally skipped and is not a release blocker. The curated machine-readable record is `evidence/official-kaggle-saved-version.json`.

## Parallel-loading qualification

On 2026-10-09, the same Kaggle T4×2 model/runtime combination was benchmarked with Hugging Face parallel loading while preserving BF16 and the qualified device map (`transformer→GPU0`, `text_encoder→GPU1`, `vae→GPU1`). The earlier fresh acceptance cold load was `736.009689181` seconds. A 2-worker run loaded in `190.432466950` seconds; a 4-worker run loaded in `125.682013119` seconds. A separate 4-worker golden validation loaded in `127.763847371` seconds, generated seed 42 in `52.131240722` seconds, and reproduced the canonical SHA-256 `56e0fca007d3da945de77788b5ab8a0a131b58730d93b624ca65e7c6ca6ea307` exactly.

The optimized notebook therefore sets `HF_ENABLE_PARALLEL_LOADING=YES` and `HF_PARALLEL_LOADING_WORKERS=4` before importing Diffusers. The final official Saved Version independently confirmed this configuration in the full production workflow, so the parallel-loading candidate is now the release acceptance notebook.

## Golden output

The accepted golden `safe_512`, seed 42 PNG has SHA-256:

`56e0fca007d3da945de77788b5ab8a0a131b58730d93b624ca65e7c6ca6ea307`

A mismatch after dependency or model changes is a signal to investigate; it should not be normalized away without explanation.

The evidence bundle is fail-closed: `scripts/verify_evidence.py` cross-checks the curated records against `qualification-summary.json` and `finalize-output.txt`, validates SHA-256 fields, requires the Quick Tunnel placeholder, and rejects leaked tunnel hostnames or Bearer credentials. `scripts/api_contract_acceptance.py` regenerates the CPU-only coordinator status-code contract deterministically; CI requires that regeneration to produce no diff. Live Kaggle runtime evidence and CPU contract evidence remain explicitly separate.

## Evidence hygiene

Evidence committed to Git must be sanitized. Never include live Bearer tokens, credential files, unredacted account data, or ephemeral tunnel hostnames. Runtime output paths may appear in qualification metadata when useful, but generated images and session state are not source artifacts.
