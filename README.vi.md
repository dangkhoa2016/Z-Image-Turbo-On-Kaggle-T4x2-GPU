# Z-Image-Turbo trên Kaggle T4×2 GPU

<p align="center">
  <a href="https://github.com/dangkhoa2016/Z-Image-Turbo-On-Kaggle-T4x2-GPU/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/dangkhoa2016/Z-Image-Turbo-On-Kaggle-T4x2-GPU/actions/workflows/ci.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/License-MIT-green.svg"></a>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white">
  <img alt="GPU" src="https://img.shields.io/badge/GPU-Tesla%20T4%20%C3%972-76B900?logo=nvidia&logoColor=white">
  <img alt="Precision" src="https://img.shields.io/badge/Precision-BF16-2563EB">
  <img alt="API" src="https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white">
  <img alt="Queue" src="https://img.shields.io/badge/GPU%20Execution-Single--flight-7C3AED">
  <img alt="Qualification" src="https://img.shields.io/badge/Qualification-PASS-0A7E07">
  <img alt="Kaggle" src="https://img.shields.io/badge/Kaggle-T4%20%C3%972-20BEFF?logo=kaggle&logoColor=white">
</p>

> 🌐 Ngôn ngữ: [English](README.md) | **Tiếng Việt**

Một dự án kỹ thuật có thể tái lập để chạy **Tongyi-MAI/Z-Image-Turbo** thành image-generation service có authentication, API-only trên **Kaggle NVIDIA Tesla T4 ×2**.

Thiết kế đã qualification giữ **một `ZImagePipeline` BF16 resident trên cả hai GPU**, serialize GPU generation qua bounded queue, expose FastAPI coordinator, lưu deterministic acceptance evidence và có thể tùy chọn chỉ expose coordinator qua Cloudflare Quick Tunnel tạm thời.

Đây là dự án kỹ thuật độc lập xây dựng quanh upstream model Z-Image-Turbo, không phải bản phát hành chính thức của Tongyi-MAI.

---

## Tổng quan nhanh

| Hạng mục | Qualified public contract |
| --- | --- |
| Model source | Kaggle mirror của `Tongyi-MAI/Z-Image-Turbo` |
| Accelerator | Đúng **2 × NVIDIA Tesla T4** |
| Precision | **BF16** |
| Logical model load | **1 resident pipeline** |
| Transformer | `cuda:0` |
| Text encoder | `cuda:1` |
| VAE | `cuda:1` |
| API | FastAPI coordinator tại `127.0.0.1:8090` |
| Internal worker | Loopback-only tại `127.0.0.1:8101` |
| GPU scheduling | **Single-flight**, bounded waiting queue |
| Profile mặc định | `safe_512` — 512×512, 9 steps, guidance 0.0 |
| Profile lớn hơn | `high_768` — 768×768, 9 steps, guidance 0.0 |
| Golden 512 | **52.483 s**, giữ SHA-256 authority |
| Qualification | **PASS** |
| License | MIT cho code/docs gốc của repository |

Hai GPU T4 cung cấp capacity cho **một logical pipeline**. Repository này **không** claim tốc độ inference gấp 2 hoặc hai serving replica độc lập.

---

## Vì sao dự án này tồn tại

Một model có thể load và sinh được một ảnh vẫn chưa phải production-style serving example. Repository này tập trung vào biên kỹ thuật của một Kaggle REST service có thể tái lập:

- giữ model hot thay vì reload theo từng request;
- phân bố một logical pipeline trên cả hai T4;
- yêu cầu Bearer authentication rõ ràng cho generation và job data;
- tách public coordinator khỏi internal GPU worker;
- serialize GPU execution để giữ trong memory envelope đã validate;
- giới hạn queue admission thay vì cho phép lượng waiting work vô hạn;
- từ chối unsupported profile trước GPU execution;
- lưu timing, memory telemetry, hash và acceptance evidence;
- giữ runtime credential và ephemeral tunnel information ngoài Git history.

Mục tiêu không chỉ là sinh được ảnh. Mục tiêu là làm serving path **có thể kiểm tra, tái lập và trung thực về giới hạn**.

---

## Kiến trúc

```text
client
  |
  | HTTPS tùy chọn
  v
Cloudflare Quick Tunnel
  |
  v
FastAPI coordinator :8090
  |
  | auth + validation + bounded admission + job state
  v
internal worker :8101
  |
  v
một BF16 ZImagePipeline resident
  |
  +-- transformer  -> cuda:0
  +-- text_encoder -> cuda:1
  +-- VAE          -> cuda:1
```

Chỉ coordinator được phép tunnel. Worker luôn loopback-only. Xem [Kiến trúc](docs/architecture.vi.md) để biết đầy đủ process, scheduling, placement và fail-closed design.

---

## REST surface

Public:

- `GET /` — service metadata;
- `GET /health` — coordinator liveness.

Có Bearer authentication:

- `GET /ready` — worker và runtime readiness;
- `GET /v1/info` — profile và runtime identity;
- `POST /v1/images/generations` — submit generation job;
- `GET /v1/jobs/{id}` — poll job state và result metadata;
- `GET /v1/jobs/{id}/image` — lấy PNG hoàn tất.

Ví dụ request body:

```json
{
  "prompt": "A quiet coastal observatory under a star-filled sky",
  "seed": 42,
  "profile": "safe_512"
}
```

Xem [REST API](docs/api.vi.md) để biết authentication và status-code contract.

---

## Profile đã qualification

| Profile | Resolution | Steps | Guidance | Trạng thái |
| --- | ---: | ---: | ---: | --- |
| `safe_512` | 512×512 | 9 | 0.0 | Mặc định, đã qualification |
| `high_768` | 768×768 | 9 | 0.0 | Single-flight đã qualification; gần memory ceiling T4 |

1024×1024 bị chủ động từ chối trước GPU execution. FP16 chủ động không được dùng làm fallback vì thí nghiệm FP16 đã validate tạo output all-black bị degenerate.

---

## Điểm nổi bật qualification

### Golden 512

`safe_512`, seed 42:

- worker inference: **52.483 s**;
- SHA-256: `56e0fca007d3da945de77788b5ab8a0a131b58730d93b624ca65e7c6ca6ea307`;
- unique colors: `90,846`;
- verdict: **PASS**.

### Resident endurance 5 job

Năm submission gần như đồng thời đi vào hệ thống với chính xác **một `running` + bốn `queued`**. Cả năm hoàn tất tuần tự với worker latency `57.391`, `55.037`, `55.735`, `56.450` và `56.237` giây.

### Mixed profile

`512 → 768 → 512` hoàn tất trong `59.134`, `127.837` và `56.352` giây. Request 512 cuối hoàn tất bình thường sau request 768 dùng memory cao hơn. Verdict: **PASS**.

### Error/security boundary

Thiếu auth → 401, auth không hợp lệ → 403, prompt rỗng → 422, unsupported 1024 profile → 422, worker vẫn ready sau đó.

Chi tiết đầy đủ: [Qualification Evidence](docs/qualification.vi.md) và [`evidence/qualification-summary.json`](evidence/qualification-summary.json).

---

## Workflow Kaggle có thể tái lập

Model đã qualification được attach dưới tên:

`dangkhoa2016/tongyi-mai-z-image-turbo/PyTorch/default/1`

và load trực tiếp từ:

`/kaggle/input/models/dangkhoa2016/tongyi-mai-z-image-turbo/pytorch/default/1`

với `local_files_only=True`.

Production notebook:

[`notebooks/kaggle-t4x2-rest-server-production.ipynb`](notebooks/kaggle-t4x2-rest-server-production.ipynb)

Identity notebook hiện tại cùng quy tắc reproducibility được ghi trong [Khả năng tái lập và evidence](docs/reproducibility.vi.md).

---

## Verification cục bộ

Các lightweight repository gate không cần GPU model weights:

```bash
PYTHONPATH=src pytest -q
python -m compileall -q src scripts tests
for file in scripts/*.sh; do bash -n "$file"; done
python scripts/verify_notebook_static.py notebooks/kaggle-t4x2-rest-server-production.ipynb
```

Live runtime claim vẫn cần fresh evidence trên Kaggle T4×2 khi qualified contract thay đổi.

---

## Tài liệu

| Chủ đề | English | Tiếng Việt |
| --- | --- | --- |
| REST API | [docs/api.md](docs/api.md) | [docs/api.vi.md](docs/api.vi.md) |
| Architecture | [docs/architecture.md](docs/architecture.md) | [docs/architecture.vi.md](docs/architecture.vi.md) |
| Kaggle runtime | [docs/kaggle-runtime.md](docs/kaggle-runtime.md) | [docs/kaggle-runtime.vi.md](docs/kaggle-runtime.vi.md) |
| Qualification | [docs/qualification.md](docs/qualification.md) | [docs/qualification.vi.md](docs/qualification.vi.md) |
| Limitations | [docs/limitations.md](docs/limitations.md) | [docs/limitations.vi.md](docs/limitations.vi.md) |
| Development | [docs/development.md](docs/development.md) | [docs/development.vi.md](docs/development.vi.md) |
| Troubleshooting | [docs/troubleshooting.md](docs/troubleshooting.md) | [docs/troubleshooting.vi.md](docs/troubleshooting.vi.md) |
| Reproducibility | [docs/reproducibility.md](docs/reproducibility.md) | [docs/reproducibility.vi.md](docs/reproducibility.vi.md) |
| Changelog | [CHANGELOG.md](CHANGELOG.md) | [CHANGELOG.vi.md](CHANGELOG.vi.md) |

Governance dưới `.github/` cũng được duy trì theo cặp English/Tiếng Việt tại các file/template mà GitHub hỗ trợ theo cách phù hợp.

---

## Chủ động không hỗ trợ

- FP16 serving fallback;
- generation 1024×1024;
- concurrent GPU generation;
- hai resident model replica độc lập;
- pipeline-per-request model reload;
- CPU inference fallback;
- runtime Hugging Face download fallback;
- stage toàn bộ model vào `/tmp`;
- HTML/Gradio inference UI;
- coi Quick Tunnel hostname là deployment URL ổn định.

Xem [Giới hạn](docs/limitations.vi.md) trước khi thay đổi các boundary này.

---

## Bảo mật

API token được sinh theo session và không bao giờ được commit, nhúng vào public URL hay copy vào evidence. Internal worker chỉ bind loopback. Quick Tunnel URL là ephemeral và bị loại khỏi release authority.

Xem [Chính sách bảo mật](.github/SECURITY.vi.md) để biết cách báo cáo và project-specific boundary.

---

## License

Code và tài liệu gốc của repository này được cấp phép theo [MIT License](LICENSE):

**Copyright (c) 2026 Đăng Khoa <i.am@dangkhoa.dev>**

Model weights không được repository này phân phối lại và vẫn chịu các điều khoản license của upstream/model host.
