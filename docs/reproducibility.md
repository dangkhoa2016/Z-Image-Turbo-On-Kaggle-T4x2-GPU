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

The current repository candidate is `notebooks/kaggle-t4x2-rest-server-production.ipynb`. Its bilingual Step workflow now embeds the current evidence-integrity scripts and verifies payload parity against the repository source tree.

Current candidate Git blob:

`84e2729214d241c5545c48d07d15514f07b0b4f6`

Current candidate SHA-256:

`934d56976b32be5fff9a88ca2e34b5a2229a03cffed74220f8bb3b7a201bf8ad`

The latest **executed Kaggle qualification checkpoint before the current evidence-integrity revision** used Git blob `dbd7ec6f7e2b20797cccdb178cb8d545e6aa8c1b` with SHA-256 `e93f5a1c48e386bf417ed7e4372cdde4dd806219218054a425f6a27b28d9964b`. That historical identity is retained deliberately and must not be relabeled as the current notebook.

The current revision changes executable evidence-handling code and the embedded payload. A fresh Kaggle Saved Version is therefore mandatory before this candidate can become the release acceptance notebook.

## Golden output

The accepted golden `safe_512`, seed 42 PNG has SHA-256:

`56e0fca007d3da945de77788b5ab8a0a131b58730d93b624ca65e7c6ca6ea307`

A mismatch after dependency or model changes is a signal to investigate; it should not be normalized away without explanation.

The evidence bundle is fail-closed: `scripts/verify_evidence.py` cross-checks the curated records against `qualification-summary.json` and `finalize-output.txt`, validates SHA-256 fields, requires the Quick Tunnel placeholder, and rejects leaked tunnel hostnames or Bearer credentials. `scripts/api_contract_acceptance.py` regenerates the CPU-only coordinator status-code contract deterministically; CI requires that regeneration to produce no diff. Live Kaggle runtime evidence and CPU contract evidence remain explicitly separate.

## Evidence hygiene

Evidence committed to Git must be sanitized. Never include live Bearer tokens, credential files, unredacted account data, or ephemeral tunnel hostnames. Runtime output paths may appear in qualification metadata when useful, but generated images and session state are not source artifacts.
