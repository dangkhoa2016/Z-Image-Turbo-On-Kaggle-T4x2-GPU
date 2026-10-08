# Runtime Kaggle

> 🌐 Ngôn ngữ: [English](kaggle-runtime.md) | **Tiếng Việt**

## Môi trường đã qualification

| Thành phần | Giá trị đã qualification |
| --- | --- |
| GPU | 2 × NVIDIA Tesla T4 |
| Python | 3.13.15 |
| PyTorch | 2.11.0+cu128 |
| CUDA runtime | 12.8 |
| diffusers | 0.40.0 |
| transformers | 5.16.1 |
| accelerate | 1.14.0 |
| dtype | BF16 |

Kaggle model được attach:

`/kaggle/input/models/dangkhoa2016/tongyi-mai-z-image-turbo/pytorch/default/1`

Server load trực tiếp từ Kaggle Input với `local_files_only=True`. Không stage toàn bộ model vào `/tmp`; direct-load path đã qualification đơn giản hơn và tránh nhân đôi dữ liệu trên disk.

## Trình tự startup

1. Attach `dangkhoa2016/tongyi-mai-z-image-turbo/PyTorch/default/1` vào notebook.
2. Xác nhận đúng hai Tesla T4.
3. Materialize source repository hoặc dùng payload trong production notebook.
4. Sinh API token theo session tại `.runtime/api_token` với permission hạn chế.
5. Start internal worker tại `127.0.0.1:8101`.
6. Chờ worker báo pipeline BF16 cùng device map kỳ vọng.
7. Start coordinator tại `127.0.0.1:8090`.
8. Chạy health/readiness và REST acceptance cục bộ.
9. Tùy chọn start Cloudflare Quick Tunnel chỉ trỏ vào port `8090`.

## Profile đã qualification

| Profile | Kích thước | Steps | Guidance | Qualification |
| --- | ---: | ---: | ---: | --- |
| `safe_512` | 512×512 | 9 | 0.0 | mặc định, đã qualification |
| `high_768` | 768×768 | 9 | 0.0 | single-flight đã qualification; gần giới hạn memory T4 |

Không expose 1024×1024. Không dùng FP16 làm automatic fallback.

## File theo session

`.runtime/` có thể chứa API token, process id, tunnel URL và binary `cloudflared` đã tải. `outputs/`, `metadata/` và log cũng chỉ là dữ liệu tạm thời. Không file nào trong số này thuộc Git history hay release archive.
