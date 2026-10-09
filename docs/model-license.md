# Model Licensing and Attribution

> Language: **English** | [Tiếng Việt](model-license.vi.md)

## Scope

This project has two separate licensing layers and they must not be conflated.

1. **Repository code and original documentation** — licensed under the repository [MIT License](../LICENSE), copyright 2026 Đăng Khoa <i.am@dangkhoa.dev>.
2. **Z-Image-Turbo upstream model and model weights** — the upstream model card for `Tongyi-MAI/Z-Image-Turbo` at the exact revision qualified by this project, `f332072aa78be7aecdf3ee76d5c247082da564a6`, declares **Apache License 2.0**.

A reference copy of Apache License 2.0 is included at [`licenses/Apache-2.0.txt`](../licenses/Apache-2.0.txt). The upstream source is https://huggingface.co/Tongyi-MAI/Z-Image-Turbo.

## Kaggle mirror

The runtime attaches the Kaggle mirror `dangkhoa2016/tongyi-mai-z-image-turbo/PyTorch/default/1` only to make the qualified notebook reproducible without a runtime Hugging Face download. The mirror is not presented as an independently authored model and does not change ownership or licensing of the upstream model.

The Git repository itself does not contain the model weight files. The MIT license in this repository therefore must not be interpreted as relicensing Z-Image-Turbo model weights under MIT.

## Attribution and redistribution

When using or redistributing the model artifacts, users should retain the applicable upstream license, copyright, attribution, and notices required by Apache License 2.0 and by any separately licensed third-party components included by the upstream distribution.

Repository-level attribution is summarized in [`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).

## No endorsement

This is an independent engineering project around Z-Image-Turbo and is not an official Tongyi-MAI release or endorsement.

This document records the licensing scope used by this repository for provenance and compliance clarity; it is not legal advice.
