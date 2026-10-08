## Tóm tắt

Mô tả thay đổi và lý do cần thiết.

> 🌐 Mẫu: [English](PULL_REQUEST_TEMPLATE.md) | **Tiếng Việt**

## Xác minh

- [ ] `PYTHONPATH=src pytest -q`
- [ ] Kiểm tra Python compile
- [ ] Kiểm tra shell syntax khi script thay đổi
- [ ] Static verify production notebook khi notebook/payload thay đổi
- [ ] Tài liệu English/Tiếng Việt được đồng bộ
- [ ] Không commit credential, runtime URL, generated output hay private artifact

## Ảnh hưởng qualification

- [ ] Không thay đổi qualified runtime contract
- [ ] Có thay đổi ảnh hưởng qualification; đã kèm hoặc liên kết evidence Kaggle T4×2 mới

## Ghi chú

Liệt kê limitation, compatibility concern hoặc follow-up work.
