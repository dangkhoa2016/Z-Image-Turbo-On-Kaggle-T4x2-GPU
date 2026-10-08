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

The current repository candidate is `notebooks/kaggle-t4x2-rest-server-production.ipynb`. Its presentation follows the repository-standard bilingual Step workflow while preserving every executable code cell and the embedded runtime payload identity.

Current candidate Git blob:

`af738025e13a8eab631f3d797537530202dab143`

Current candidate SHA-256:

`c2a68605cee4a841f840a9c7af2a62c5404411ffcbbae98cd164c79d7a93352f`

The latest **executed Kaggle qualification checkpoint before this presentation-only revision** used Git blob `dbd7ec6f7e2b20797cccdb178cb8d545e6aa8c1b` with SHA-256 `e93f5a1c48e386bf417ed7e4372cdde4dd806219218054a425f6a27b28d9964b`. That historical identity is retained here deliberately; it must not be silently relabeled as the new notebook.

The presentation revision does not change the executable code cells or embedded payload authority, but a fresh Kaggle Saved Version is still required before the current candidate is promoted as the release acceptance notebook.

## Golden output

The accepted golden `safe_512`, seed 42 PNG has SHA-256:

`56e0fca007d3da945de77788b5ab8a0a131b58730d93b624ca65e7c6ca6ea307`

A mismatch after dependency or model changes is a signal to investigate; it should not be normalized away without explanation.

## Evidence hygiene

Evidence committed to Git must be sanitized. Never include live Bearer tokens, credential files, unredacted account data, or ephemeral tunnel hostnames. Runtime output paths may appear in qualification metadata when useful, but generated images and session state are not source artifacts.
