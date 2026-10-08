# Kiến trúc

> 🌐 Ngôn ngữ: [English](architecture.md) | **Tiếng Việt**

## Mục tiêu thiết kế

Expose Z-Image-Turbo thành một REST service nhỏ theo phong cách production trên Kaggle T4×2 nhưng không đánh đồng hai GPU với hai replica độc lập hoặc tốc độ sinh ảnh gấp đôi. Thiết kế đã validate giữ một logical pipeline BF16 resident trên cả hai GPU và serialize generation.

## Mô hình process

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
  | bounded admission + job state
  v
internal worker :8101
  |
  v
một ZImagePipeline resident
  |
  +-- transformer  -> cuda:0
  +-- text_encoder -> cuda:1
  +-- vae          -> cuda:1
```

Coordinator và worker đều bind loopback. Chỉ coordinator được phép tunnel. Worker không bao giờ được chủ động expose.

## Phân bố GPU

Device map đã qualification:

- `transformer` → GPU0
- `text_encoder` → GPU1
- `vae` → GPU1

Pipeline là một logical model load trải trên hai Tesla T4. Đây là phân bố capacity, không phải data-parallel để tăng throughput.

## Scheduling

`JobManager` sở hữu một background execution thread. Admission dùng bounded semaphore đại diện cho một generation đang active cộng waiting capacity đã cấu hình. Worker có thêm non-blocking lock như single-flight guard thứ hai.

Thiết kế chủ động từ chối parallel GPU generation vì memory envelope đã validate chỉ dành cho một resident pipeline và một active inference trajectory.

## Startup fail-closed

Startup kiểm tra:

1. CUDA khả dụng.
2. Có ít nhất hai GPU.
3. Cả hai device phát hiện được là Tesla T4.
4. Kaggle model mount tồn tại.
5. Model chỉ load từ local files.
6. `hf_device_map` khớp chính xác qualified placement.

Không dùng CPU fallback hay network model download để che một preflight thất bại.

## Runtime storage

PNG live được ghi vào `outputs/`, JSON theo request vào `metadata/`, và session state vào `.runtime/`. Các path này bị ignore và không phải release authority. Evidence đã sanitize và curate nằm trong `evidence/`.
