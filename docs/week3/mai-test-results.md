# KẾT QUẢ KIỂM THỬ CV – TUẦN 3

**Sinh viên:** Nguyễn Thị Trúc Mai – 24110284  
**Đề tài:** Nền tảng tuyển dụng – Lọc CV tự động

## 1. Mục tiêu

Kiểm thử khả năng trích xuất thông tin ứng viên từ nhiều mẫu CV PDF có bố cục khác nhau bằng Amazon S3, Amazon Textract và AWS Lambda.

## 2. Môi trường kiểm thử

- S3 Bucket: `cv-recruitment-ute-2026-2027`
- Thư mục CV: `cvs/`
- Lambda Function: `cv-process`
- Dịch vụ OCR: Amazon Textract
- Giám sát: Amazon CloudWatch Logs
- Region: `us-east-1`

## 3. Kết quả kiểm thử thực tế

| CV | Họ tên | Email/SĐT | Kỹ năng | Kinh nghiệm | Kết quả |
|---|---|---|---|---|---|
| Vũ Văn Hiếu | Đạt | Đạt | Đạt | Đạt | Đạt |
| Trần Bảo Duy | Đạt | Đạt | Đạt | Đạt | Đạt |
| Nguyễn Đăng Khanh | Đạt | Đạt | Đạt | Đạt | Đạt |
| Vũ Xuân Tài | Đạt | Đạt | Đạt | Đạt | Đạt |

## 4. Ghi nhận kết quả từng CV

### 4.1. CV Vũ Văn Hiếu
- Họ tên: `VU VAN HIEU`
- Email: `hello@reallygreatsite.com`
- Số điện thoại: `0903414848`
- Kỹ năng: `java`, `sql`
- Kinh nghiệm: `Total Experience: 6 months`
- ExperienceYears: `0.5`
- Nhận xét: Lambda trích xuất đúng các thông tin chính.

### 4.2. CV Trần Bảo Duy
- Họ tên: `TRAN BAO DUY`
- Email: `tranbaoduy@example.com`
- Số điện thoại: `0912345678`
- Kỹ năng trích xuất được: `aws`, `docker`, `git`, `java`, `mysql`, `rest api`, `spring boot` ...
- Nhận xét: Lambda nhận diện đúng họ tên, email, số điện thoại và nhiều kỹ năng chính trong CV.

### 4.3. CV Nguyễn Đăng Khanh
- Họ tên: `NGUYEN DANG KHANH`
- Email: `ndkhanh@gmai.com`
- Số điện thoại: `0903414848`
- Kỹ năng: `git`, `java`, `rest api`, `spring boot`, `sql`
- Kinh nghiệm: `6 months of practical experience`
- Nhận xét: Lambda trích xuất đúng thông tin chính, kết quả ổn định.

### 4.4. CV Vũ Xuân Tài
- Họ tên: `VU XUAN TAI`
- Email: `vxtai@gmail.com`
- Số điện thoại: `0903414848`
- Kỹ năng trích xuất được: `aws`, `css`, `docker`, `git`, `hibernate`, `html` ...
- Nhận xét: Lambda nhận diện đúng ứng viên và trích xuất được nhiều kỹ năng phù hợp.

## 5. Lỗi phát hiện và cách xử lý

| Nội dung | Kết quả |
|---|---|
| Lỗi deploy Lambda | Không có |
| Lỗi test event | Không có |
| Lỗi chạy Textract | Không có |
| Lỗi CloudWatch nghiêm trọng | Không có |
| Ghi nhận hạn chế | Một số CV trả về danh sách kỹ năng dài, theo cơ chế dò từ khóa nên cần tiếp tục tinh chỉnh để kết quả gọn hơn |

## 6. Minh chứng

Ảnh lưu tại thư mục: `screenshots/week3/`

- Lambda đã cập nhật code và deploy thành công.
- Đã kiểm thử thực tế 4 CV:
  - Vũ Văn Hiếu
  - Trần Bảo Duy
  - Nguyễn Đăng Khanh
  - Vũ Xuân Tài
- Kết quả trả về đều ở trạng thái `Executing function: succeeded`.

## 7. Kết luận

Trong tuần 3, chức năng trích xuất CV của Mai đã được kiểm thử với 4 mẫu CV có bố cục khác nhau. Kết quả cho thấy Lambda kết hợp Textract có thể đọc được họ tên, email, số điện thoại, kỹ năng và kinh nghiệm của ứng viên. Các lần kiểm thử đều chạy thành công, chưa phát sinh lỗi nghiêm trọng. Tuy nhiên, phần kỹ năng hiện vẫn dựa trên đối sánh từ khóa nên ở một số CV danh sách kỹ năng trả về còn dài và cần tinh chỉnh thêm ở tuần sau.