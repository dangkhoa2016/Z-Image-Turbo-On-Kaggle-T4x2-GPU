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

Candidate hiện tại trong repository là `notebooks/kaggle-t4x2-rest-server-production.ipynb`. Workflow Step song ngữ giữ nguyên embedded payload 30 file đã audit, đồng thời bật launch environment cho Hugging Face parallel loading đã qualification trước khi import Diffusers.

Git blob của candidate hiện tại:

`64f4b40b7dcb65b8f258505931d7ecf40c615402`

SHA-256 của candidate hiện tại:

`1aeaefb88b325ac068f996e7f1e6aaaf5f6e73e1fcf5b6de363d3426bd129d33`

Embedded payload SHA-256 vẫn là `3297e31dc53177e547d09b3d33febc2ebb46aba305398272dc9899d6528e3cfe`; manifest SHA-256 vẫn là `5fbc29b146223409db3f97dc6619a6e68df78a386a4cd3c5689406c4e44bcb66` với 30 file.

Release acceptance run là một fresh Kaggle Saved Version chạy từ source candidate đã tối ưu hiện tại (SHA-256 `1aeaefb88b325ac068f996e7f1e6aaaf5f6e73e1fcf5b6de363d3426bd129d33`) trên tài khoản Kaggle chính thức của chủ dự án. Executed notebook artifact tải về có SHA-256 `488f881fbcd006e40de529d1e8c27a76f869a5370b0c97e4fcc3f3d041976599`: cả 11 code cell đều chạy, không có error output, có chín PNG được embed và run kết thúc với `FINAL_QUALIFICATION=PASS` cùng `EVIDENCE_VERIFY=PASS`.

Cùng run này xác nhận `HF_ENABLE_PARALLEL_LOADING=YES` với bốn worker, thời gian load model `124.084353364` giây, BF16 device map đã qualification, golden SHA-256 chính xác `56e0fca007d3da945de77788b5ab8a0a131b58730d93b624ca65e7c6ca6ea307`, five-job queue endurance, live error boundaries và mixed qualification `512→768→512`. Optional public Quick Tunnel gate được chủ động bỏ qua và không phải release blocker. Record machine-readable đã curate nằm tại `evidence/official-kaggle-saved-version.json`.

## Qualification parallel loading

Ngày 2026-10-09, cùng tổ hợp model/runtime Kaggle T4×2 được benchmark với Hugging Face parallel loading trong khi vẫn giữ BF16 và device map đã qualification (`transformer→GPU0`, `text_encoder→GPU1`, `vae→GPU1`). Cold load của fresh acceptance trước đó là `736.009689181` giây. Cấu hình 2 worker load trong `190.432466950` giây; cấu hình 4 worker load trong `125.682013119` giây. Một golden validation độc lập với 4 worker load trong `127.763847371` giây, sinh seed 42 trong `52.131240722` giây và tái tạo chính xác canonical SHA-256 `56e0fca007d3da945de77788b5ab8a0a131b58730d93b624ca65e7c6ca6ea307`.

Vì vậy notebook đã tối ưu đặt `HF_ENABLE_PARALLEL_LOADING=YES` và `HF_PARALLEL_LOADING_WORKERS=4` trước khi import Diffusers. Official Saved Version cuối cùng đã xác nhận độc lập cấu hình này trong full production workflow, vì vậy candidate parallel-loading hiện là release acceptance notebook.

## Golden output

PNG `safe_512`, seed 42 đã accepted có SHA-256:

`56e0fca007d3da945de77788b5ab8a0a131b58730d93b624ca65e7c6ca6ea307`

Nếu digest thay đổi sau khi đổi dependency hoặc model, cần điều tra; không nên âm thầm coi khác biệt là bình thường.

Evidence bundle dùng cơ chế fail-closed: `scripts/verify_evidence.py` đối chiếu chéo các record đã curate với `qualification-summary.json` và `finalize-output.txt`, kiểm tra các trường SHA-256, bắt buộc dùng placeholder cho Quick Tunnel và từ chối tunnel hostname hoặc Bearer credential bị lộ. `scripts/api_contract_acceptance.py` tái tạo deterministic status-code contract của coordinator trên CPU; CI yêu cầu lần tái tạo này không tạo ra diff. Evidence từ Kaggle runtime thật và evidence contract trên CPU được giữ tách biệt rõ ràng.

## Evidence hygiene

Evidence commit vào Git phải được sanitize. Không bao giờ đưa live Bearer token, credential file, account data chưa che hoặc ephemeral tunnel hostname vào repository. Runtime output path có thể xuất hiện trong qualification metadata khi hữu ích, nhưng generated image và session state không phải source artifact.
