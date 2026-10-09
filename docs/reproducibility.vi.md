# Khả năng tái lập và Evidence

> 🌐 Ngôn ngữ: [English](reproducibility.md) | **Tiếng Việt**

## Authority là gì

Các tuyên bố runtime hướng tới release dựa trên:

- source tree chính xác;
- production notebook;
- các record đã curate trong `evidence/`;
- Kaggle model variation/version đã pin;
- môi trường phần mềm và phần cứng đã qualification.

Screenshot đẹp hoặc tunnel URL tạm thời không phải authority.

## Identity của production notebook

Candidate hiện tại trong repository là `notebooks/kaggle-t4x2-rest-server-production.ipynb`. Workflow Step song ngữ hiện embed các script evidence-integrity mới nhất và kiểm tra payload parity với source tree của repository.

Git blob của candidate hiện tại:

`84e2729214d241c5545c48d07d15514f07b0b4f6`

SHA-256 của candidate hiện tại:

`934d56976b32be5fff9a88ca2e34b5a2229a03cffed74220f8bb3b7a201bf8ad`

**Executed Kaggle qualification checkpoint gần nhất trước evidence-integrity revision hiện tại** dùng Git blob `dbd7ec6f7e2b20797cccdb178cb8d545e6aa8c1b` với SHA-256 `e93f5a1c48e386bf417ed7e4372cdde4dd806219218054a425f6a27b28d9964b`. Identity lịch sử này được giữ lại có chủ ý và không được đổi nhãn thành notebook hiện tại.

Revision hiện tại thay đổi executable evidence-handling code và embedded payload. Vì vậy bắt buộc chạy một fresh Kaggle Saved Version trước khi candidate này được nâng thành release acceptance notebook.

## Golden output

PNG `safe_512`, seed 42 đã accepted có SHA-256:

`56e0fca007d3da945de77788b5ab8a0a131b58730d93b624ca65e7c6ca6ea307`

Nếu digest thay đổi sau khi đổi dependency hoặc model, cần điều tra; không nên âm thầm coi khác biệt là bình thường.

Evidence bundle dùng cơ chế fail-closed: `scripts/verify_evidence.py` đối chiếu chéo các record đã curate với `qualification-summary.json` và `finalize-output.txt`, kiểm tra các trường SHA-256, bắt buộc dùng placeholder cho Quick Tunnel và từ chối tunnel hostname hoặc Bearer credential bị lộ. `scripts/api_contract_acceptance.py` tái tạo deterministic status-code contract của coordinator trên CPU; CI yêu cầu lần tái tạo này không tạo ra diff. Evidence từ Kaggle runtime thật và evidence contract trên CPU được giữ tách biệt rõ ràng.

## Evidence hygiene

Evidence commit vào Git phải được sanitize. Không bao giờ đưa live Bearer token, credential file, account data chưa che hoặc ephemeral tunnel hostname vào repository. Runtime output path có thể xuất hiện trong qualification metadata khi hữu ích, nhưng generated image và session state không phải source artifact.
