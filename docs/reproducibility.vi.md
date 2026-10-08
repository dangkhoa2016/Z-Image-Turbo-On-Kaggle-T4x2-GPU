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

Candidate hiện tại trong repository là `notebooks/kaggle-t4x2-rest-server-production.ipynb`. Presentation đã được chuẩn hóa theo workflow Step song ngữ thống nhất với các repository khác, trong khi toàn bộ executable code cell và embedded runtime payload identity được giữ nguyên.

Git blob của candidate hiện tại:

`af738025e13a8eab631f3d797537530202dab143`

SHA-256 của candidate hiện tại:

`c2a68605cee4a841f840a9c7af2a62c5404411ffcbbae98cd164c79d7a93352f`

**Executed Kaggle qualification checkpoint gần nhất trước presentation-only revision này** dùng Git blob `dbd7ec6f7e2b20797cccdb178cb8d545e6aa8c1b` với SHA-256 `e93f5a1c48e386bf417ed7e4372cdde4dd806219218054a425f6a27b28d9964b`. Identity lịch sử này được giữ lại có chủ ý; không được đổi nhãn thành notebook mới một cách im lặng.

Presentation revision không thay đổi executable code cell hay embedded payload authority, nhưng vẫn cần một fresh Kaggle Saved Version trước khi candidate hiện tại được nâng thành release acceptance notebook.

## Golden output

PNG `safe_512`, seed 42 đã accepted có SHA-256:

`56e0fca007d3da945de77788b5ab8a0a131b58730d93b624ca65e7c6ca6ea307`

Nếu digest thay đổi sau khi đổi dependency hoặc model, cần điều tra; không nên âm thầm coi khác biệt là bình thường.

## Evidence hygiene

Evidence commit vào Git phải được sanitize. Không bao giờ đưa live Bearer token, credential file, account data chưa che hoặc ephemeral tunnel hostname vào repository. Runtime output path có thể xuất hiện trong qualification metadata khi hữu ích, nhưng generated image và session state không phải source artifact.
