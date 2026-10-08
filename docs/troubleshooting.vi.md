# Xử lý sự cố

> 🌐 Ngôn ngữ: [English](troubleshooting.md) | **Tiếng Việt**

## `/ready` trả 503

Kiểm tra internal worker có đang chạy và xem sanitized log của worker. Startup fail-closed nếu máy không có hai Tesla T4, Kaggle model mount bị thiếu, model load thất bại hoặc device map sau load khác qualified map.

## Authentication trả 401 hoặc 403

401 nghĩa là thiếu Bearer header. 403 nghĩa là đã gửi token nhưng không khớp token của session hiện tại. Không khôi phục token từ Git history; chỉ sinh/đọc token session-local hiện tại trong `.runtime/`.

## Generation trả 429

Bounded queue đã đầy. Chờ một job đã admission hoàn tất rồi mới gửi request khác. Tăng queue size không làm tăng GPU execution concurrency.

## Image endpoint trả 409

Job tồn tại nhưng chưa hoàn tất. Poll `GET /v1/jobs/{id}` đến khi state thành `complete`, sau đó mới request image.

## 768 thất bại sau khi đổi runtime dependency

Hãy coi đây là qualification regression. Không âm thầm hạ check hoặc tiếp tục claim `high_768` được hỗ trợ. Reproduce trên T4×2, thu memory/timing evidence và chỉ cập nhật supported surface sau rerun thành công.

## Tunnel URL ngừng hoạt động

Quick Tunnel endpoint là tạm thời. Restart `cloudflared` hoặc Kaggle session có thể sinh hostname khác. Repository chủ động không persist live URL.

## Notebook static verification thất bại

Chạy:

```bash
python scripts/verify_notebook_static.py notebooks/kaggle-t4x2-rest-server-production.ipynb
```

Nếu payload hash hoặc expected file thay đổi, hãy điều tra source tree và notebook materialization logic thay vì bypass verifier.
