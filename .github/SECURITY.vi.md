# Chính sách bảo mật

> 🌐 Ngôn ngữ: [English](SECURITY.md) | **Tiếng Việt**

## Phạm vi được hỗ trợ

Dự án nhận báo cáo bảo mật cho nhánh `main` hiện tại và bản phát hành mới nhất.

## Báo cáo lỗ hổng

Không mở public issue cho lỗ hổng chưa công bố hoặc credential bị lộ. Hãy liên hệ **Đăng Khoa <i.am@dangkhoa.dev>** với bước tái hiện ngắn gọn, đường dẫn bị ảnh hưởng, mức tác động và đề xuất giảm thiểu nếu có.

## Biên bảo mật riêng của dự án

- Các endpoint có authentication yêu cầu Bearer token theo từng session.
- GPU worker nội bộ chỉ bind `127.0.0.1` và không được thiết kế để public trực tiếp.
- Cloudflare Quick Tunnel là tùy chọn và tạm thời; tunnel URL không phải authority data và không được commit.
- Model weights được mount cục bộ từ Kaggle và không được repository phân phối lại.
- Runtime secret, output sinh ra, metadata, log và trạng thái `.runtime/` bị loại khỏi source control theo thiết kế.
