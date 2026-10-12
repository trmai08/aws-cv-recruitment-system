
# Thiết kế kiến trúc hệ thống

## 1. Kiến trúc tổng quan

Hệ thống sử dụng kiến trúc Serverless trên AWS để tiếp nhận, xử lý và đánh giá CV tự động.

Sơ đồ kiến trúc tổng quan được lưu trong thư mục `Architectural diagram`.

## 2. Luồng xử lý CV

Ứng viên
↓
Upload CV PDF
↓
Amazon S3
↓
S3 ObjectCreated Event
↓
AWS Lambda
↓
Amazon Textract
↓
Lambda phân tích nội dung CV
↓
Trích xuất Skills và Experience
↓
So sánh với yêu cầu Job
↓
Tính điểm phù hợp
↓
Amazon DynamoDB

## 3. Mục tiêu kiến trúc

- Tự động hóa quá trình tiếp nhận và xử lý CV.
- Sử dụng các dịch vụ AWS để giảm công việc quản lý máy chủ.
- Lưu trữ CV và kết quả đánh giá.
- Hỗ trợ mở rộng hệ thống trong tương lai.
