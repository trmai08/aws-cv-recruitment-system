
# Thiết kế cơ sở dữ liệu DynamoDB

## 1. Bảng Jobs

Lưu trữ thông tin tuyển dụng.

| Thuộc tính | Mô tả |
|---|---|
| jobId | Mã công việc |
| title | Tên vị trí tuyển dụng |
| description | Mô tả công việc |
| requiredSkills | Danh sách kỹ năng yêu cầu |
| minExperience | Số năm kinh nghiệm yêu cầu |
| createdAt | Thời gian tạo |

## 2. Bảng Candidates

Lưu trữ thông tin ứng viên.

| Thuộc tính | Mô tả |
|---|---|
| candidateId | Mã ứng viên |
| jobId | Mã công việc ứng tuyển |
| name | Họ tên ứng viên |
| email | Email ứng viên |
| cvKey | Đường dẫn đối tượng CV trên S3 |
| skills | Danh sách kỹ năng nhận diện |
| experience | Số năm kinh nghiệm |

## 3. Bảng Results

Lưu trữ kết quả đánh giá CV.

| Thuộc tính | Mô tả |
|---|---|
| jobId | Mã công việc |
| candidateId | Mã ứng viên |
| matchedSkills | Kỹ năng phù hợp |
| missingSkills | Kỹ năng còn thiếu |
| skillScore | Điểm kỹ năng |
| experienceScore | Điểm kinh nghiệm |
| totalScore | Tổng điểm |
