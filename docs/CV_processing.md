
# Phân tích CV và công thức chấm điểm

## 1. Danh sách kỹ năng dự kiến

Java, Spring Boot, Python, JavaScript, React, Angular, SQL, MySQL, SQL Server, PostgreSQL, MongoDB, Docker, Kubernetes, AWS, Git, REST API, Microservices, HTML, CSS, C#, .NET.

## 2. Xử lý nội dung CV

- Trích xuất văn bản từ CV PDF.
- Nhận diện các kỹ năng xuất hiện trong CV.
- Xác định số năm kinh nghiệm của ứng viên.
- So sánh kỹ năng với yêu cầu công việc.
- Xác định kỹ năng phù hợp và còn thiếu.
- Tính điểm đánh giá ứng viên.

## 3. Công thức tính điểm

### Skill Score

Skill Score = (Số kỹ năng phù hợp / Tổng kỹ năng yêu cầu) × 70

Điểm kỹ năng tối đa: 70 điểm.

### Experience Score

Experience Score = min(Kinh nghiệm CV / Kinh nghiệm yêu cầu, 1) × 30

Điểm kinh nghiệm tối đa: 30 điểm.

### Total Score

Total Score = Skill Score + Experience Score

Tổng điểm tối đa: 100 điểm.

## 4. Xếp hạng ứng viên

Ứng viên được xếp hạng theo tổng điểm đánh giá từ cao xuống thấp.

Lưu ý: Cần bổ sung quy tắc xử lý trường hợp không có kỹ năng yêu cầu hoặc số năm kinh nghiệm yêu cầu bằng 0.
