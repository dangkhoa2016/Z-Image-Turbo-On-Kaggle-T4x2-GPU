# License và Attribution của Model

> Ngôn ngữ: [English](model-license.md) | **Tiếng Việt**

## Phạm vi

Dự án này có hai lớp license riêng biệt và không được gộp chúng thành một.

1. **Code và tài liệu gốc của repository** — được cấp phép theo [MIT License](../LICENSE) của repository, copyright 2026 Đăng Khoa <i.am@dangkhoa.dev>.
2. **Upstream model Z-Image-Turbo và model weights** — model card upstream của `Tongyi-MAI/Z-Image-Turbo` tại đúng revision mà dự án đã qualification, `f332072aa78be7aecdf3ee76d5c247082da564a6`, khai báo **Apache License 2.0**.

Bản tham chiếu Apache License 2.0 được lưu tại [`licenses/Apache-2.0.txt`](../licenses/Apache-2.0.txt). Nguồn upstream là https://huggingface.co/Tongyi-MAI/Z-Image-Turbo.

## Kaggle mirror

Runtime attach Kaggle mirror `dangkhoa2016/tongyi-mai-z-image-turbo/PyTorch/default/1` chỉ nhằm giúp notebook đã qualification có thể tái lập mà không phải download từ Hugging Face khi runtime đang chạy. Mirror này không được trình bày như một model do dự án tự tạo và không làm thay đổi quyền sở hữu hay license của upstream model.

Git repository này không chứa các file model weights. Vì vậy MIT license của repository không được hiểu là việc relicense model weights Z-Image-Turbo sang MIT.

## Attribution và redistribution

Khi sử dụng hoặc phân phối lại model artifact, người dùng cần giữ các license, copyright, attribution và notice áp dụng theo Apache License 2.0, cùng các điều khoản của bất kỳ third-party component nào được upstream phân phối riêng theo license khác.

Attribution ở cấp repository được tổng hợp trong [`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md).

## Không đại diện cho upstream

Đây là dự án kỹ thuật độc lập xây dựng quanh Z-Image-Turbo, không phải release hay endorsement chính thức của Tongyi-MAI.

Tài liệu này ghi lại phạm vi license mà repository sử dụng để làm rõ provenance và compliance; đây không phải tư vấn pháp lý.
