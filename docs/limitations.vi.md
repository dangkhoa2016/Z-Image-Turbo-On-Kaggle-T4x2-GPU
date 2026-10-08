# Giới hạn

> 🌐 Ngôn ngữ: [English](limitations.md) | **Tiếng Việt**

Dự án chủ động công bố ranh giới đã validate thay vì âm thầm mở rộng phạm vi hỗ trợ.

## Precision không hỗ trợ

FP16 không phải fallback. Trong quá trình qualification, FP16 path đã thử nghiệm tạo output all-black bị degenerate, vì vậy public contract chỉ giữ BF16.

## Resolution không hỗ trợ

1024×1024 không được expose thành profile. Qualification trước đó đã gặp GPU out-of-memory, do đó coordinator từ chối unsupported profile trước GPU execution.

## Không parallel generation

Hai GPU T4 chứa các component khác nhau của cùng một logical pipeline. Chúng không phải các model replica riêng. GPU generation vẫn single-flight kể cả khi nhiều REST request đang chờ.

## Memory margin của 768

`high_768` đã PASS mixed-profile qualification nhưng hoạt động gần memory ceiling của Tesla T4. Profile này chỉ qualification cho single-flight, không phải evidence rằng dimension lớn tùy ý đều an toàn.

## Networking tạm thời

Cloudflare Quick Tunnel hữu ích cho acceptance testing nhưng không phải production endpoint bền vững. Hostname sinh ra có thể thay đổi giữa các session và được chủ động loại khỏi authority artifact.

## Lifecycle của Kaggle

Kaggle session là ephemeral. Service, token, tunnel, ảnh sinh ra, log và model trong memory sẽ mất khi session kết thúc trừ khi user chủ động lưu các artifact được phép.

## Phạm vi CI

GitHub Actions validate source contract, test, shell syntax, notebook structure và repository hygiene mà không có runtime T4×2. CI CPU/static màu xanh không thay thế fresh live GPU evidence khi runtime behavior thay đổi.
