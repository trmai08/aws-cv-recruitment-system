
import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit, parse_qs, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

# ==========================================
# CAU HINH AWS
# ==========================================

REGION = "us-east-1"

# Neu API co stage dev, them /dev vao cuoi URL
API_BASE = (
    "https://k9f47vs8u9.execute-api."
    "us-east-1.amazonaws.com"
)

PROFILE = "cv-lab"

# ==========================================
# GIAO DIEN NHA TUYEN DUNG
# ==========================================

HTML = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport"
      content="width=device-width, initial-scale=1">

<title>CV Recruitment Dashboard</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #f2f6fb;
    color: #172c49;
    font-family: Arial, sans-serif;
}

header {
    background: linear-gradient(110deg,#123961,#205e95);
    color: white;
    padding: 30px 7%;
}

header h1 {
    margin: 10px 0;
}

header p {
    opacity: 0.85;
}

main {
    max-width: 1150px;
    margin: 30px auto;
    padding: 0 18px;
}

.panel {
    background: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 5px 20px #15395b12;
}

.controls {
    display: flex;
    gap: 12px;
    align-items: end;
    flex-wrap: wrap;
}

.field {
    flex: 1;
    min-width: 230px;
}

label {
    display: block;
    font-weight: bold;
    margin-bottom: 8px;
}

input {
    width: 100%;
    height: 43px;
    border: 1px solid #c4d3e1;
    border-radius: 8px;
    padding: 10px;
}

button {
    background: #146cbd;
    color: white;
    padding: 12px 22px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
}

button:disabled {
    opacity: 0.6;
}

.metrics {
    display: grid;
    grid-template-columns: repeat(3,1fr);
    gap: 15px;
    margin: 22px 0;
}

.metric {
    padding: 20px;
    border: 1px solid #e0e8f0;
    border-radius: 12px;
}

.metric span {
    color: #647891;
}

.metric strong {
    display: block;
    font-size: 28px;
    margin-top: 8px;
}

.table-wrap {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    min-width: 760px;
}

th, td {
    padding: 14px;
    text-align: left;
    border-bottom: 1px solid #e8eef5;
}

th {
    background: #f6f9fd;
    color: #58708a;
}

.rank {
    color: #135d9e;
    font-weight: bold;
}

.score {
    color: #087457;
    font-weight: bold;
}

.status {
    color: #245b91;
}

#message {
    margin-top: 15px;
    color: #526b86;
}

footer {
    color: #71839a;
    padding: 20px;
}

@media(max-width:600px) {
    .metrics {
        grid-template-columns: 1fr;
    }
}
</style>
</head>

<body>

<header>
    <small>CV RECRUITMENT SYSTEM — AWS</small>
    <h1>Bảng xếp hạng ứng viên</h1>
    <p>
        Đánh giá CV theo 70% kỹ năng
        và 30% kinh nghiệm
    </p>
</header>

<main>
<section class="panel">

<div class="controls">
    <div class="field">
        <label for="job">Vị trí tuyển dụng</label>
        <input id="job"
               value="java-backend"
               placeholder="Nhập Job ID">
    </div>

    <button id="load" onclick="loadRanking()">
        Xem xếp hạng
    </button>
</div>

<p id="message">
    Nhấn Xem xếp hạng để tải dữ liệu từ AWS.
</p>

<div class="metrics">
    <div class="metric">
        <span>Tổng số ứng viên</span>
        <strong id="total">—</strong>
    </div>

    <div class="metric">
        <span>Điểm cao nhất</span>
        <strong id="top">—</strong>
    </div>

    <div class="metric">
        <span>Điểm trung bình</span>
        <strong id="average">—</strong>
    </div>
</div>

<div class="table-wrap">
<table>
    <thead>
        <tr>
            <th>Hạng</th>
            <th>Ứng viên</th>
            <th>Kỹ năng phù hợp</th>
            <th>Kinh nghiệm</th>
            <th>Điểm kỹ năng</th>
            <th>Điểm kinh nghiệm</th>
            <th>Tổng điểm</th>
            <th>Trạng thái</th>
        </tr>
    </thead>

    <tbody id="results"></tbody>
</table>
</div>

</section>

<footer>
    Dữ liệu từ API Gateway → Lambda cv-score → DynamoDB
</footer>
</main>

<script>
function setText(id, value) {
    document.getElementById(id).textContent = value;
}

function addCell(row, value, className = "") {
    const td = document.createElement("td");
    td.textContent = String(value ?? "—");
    td.className = className;
    row.appendChild(td);
}

function number(value) {
    const n = Number(value);
    return Number.isFinite(n) ? n.toFixed(2) : "—";
}

async function loadRanking() {
    const job = document.getElementById("job").value.trim();
    const button = document.getElementById("load");

    if (!/^[a-z0-9][a-z0-9-]{0,62}$/.test(job)) {
        setText("message", "Job ID không hợp lệ.");
        return;
    }

    button.disabled = true;
    setText("message", "Đang tải dữ liệu từ AWS...");

    try {
        const response = await fetch(
            "/api/ranking?jobId=" + encodeURIComponent(job),
            {cache: "no-store"}
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Không thể gọi API");
        }

        const items = data.items || [];
        const tbody = document.getElementById("results");

        tbody.replaceChildren();

        const scores = [];

        for (const [index, item] of items.entries()) {
            const row = document.createElement("tr");
            const score = Number(item.totalScore);

            scores.push(score);

            addCell(row, item.rank ?? index + 1, "rank");
            addCell(row, item.name);
            addCell(
                row,
                (item.matchedSkills || []).join(", ") || "—"
            );
            addCell(
                row,
                item.experienceYears == null
                    ? "Chưa rõ"
                    : item.experienceYears + " năm"
            );
            addCell(row, number(item.skillScore));
            addCell(row, number(item.experienceScore));
            addCell(row, number(item.totalScore), "score");
            addCell(row, item.extractionStatus, "status");

            tbody.appendChild(row);
        }

        const average = scores.length
            ? scores.reduce((a,b) => a+b, 0) / scores.length
            : 0;

        setText("total", data.count ?? items.length);
        setText(
            "top",
            scores.length ? number(Math.max(...scores)) : "—"
        );
        setText(
            "average",
            scores.length ? number(average) : "—"
        );

        const ordered = scores.every(
            (value, index) =>
                index === 0 || scores[index-1] >= value
        );

        setText(
            "message",
            "Đã tải " + items.length + " ứng viên. " +
            (ordered
                ? "Kết quả sắp xếp đúng."
                : "Cảnh báo: thứ tự điểm chưa đúng.")
        );

    } catch (error) {
        setText("message", "Lỗi: " + error.message);
    } finally {
        button.disabled = false;
    }
}
</script>

</body>
</html>
"""

# ==========================================
# BACKEND GOI API GATEWAY
# ==========================================

class Handler(BaseHTTPRequestHandler):

    def respond(self, status, data, content_type=None):
        if isinstance(data, (dict, list)):
            data = json.dumps(
                data, ensure_ascii=False
            )

        body = data.encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            content_type or "application/json; charset=utf-8"
        )
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):

        parsed = urlsplit(self.path)

        if parsed.path == "/":
            return self.respond(
                200, HTML, "text/html; charset=utf-8"
            )

        if parsed.path != "/api/ranking":
            return self.respond(
                404, {"error": "Not found"}
            )

        job = parse_qs(
            parsed.query
        ).get("jobId", [""])[0]

        if not re.fullmatch(
            r"[a-z0-9][a-z0-9-]{0,62}", job
        ):
            return self.respond(
                400, {"error": "Job ID không hợp lệ"}
            )

        try:
            session = boto3.Session(
                profile_name=PROFILE,
                region_name=REGION
            )

            credentials = session.get_credentials()

            if credentials is None:
                return self.respond(
                    503,
                    {"error": "Chưa có AWS credentials"}
                )

            url = (
                API_BASE.rstrip("/")
                + "/jobs/"
                + quote(job)
                + "/candidates"
            )

            aws_request = AWSRequest(
                method="GET",
                url=url
            )

            SigV4Auth(
                credentials.get_frozen_credentials(),
                "execute-api",
                REGION
            ).add_auth(aws_request)

            request = Request(
                url,
                headers=dict(
                    aws_request.headers.items()
                ),
                method="GET"
            )

            with urlopen(request, timeout=25) as response:
                data = json.loads(
                    response.read().decode("utf-8")
                )

            if (
                not isinstance(data, dict)
                or not isinstance(data.get("items"), list)
            ):
                raise ValueError(
                    "API trả về dữ liệu ranking không hợp lệ"
                )

            return self.respond(200, data)

        except HTTPError as error:
            return self.respond(
                502,
                {
                    "error":
                    f"API Gateway trả HTTP {error.code}. "
                    "Kiểm tra IAM, Stage và Lambda."
                }
            )

        except Exception as error:
            print("Dashboard error:", type(error).__name__)
            return self.respond(
                502,
                {
                    "error":
                    f"Không tải được dữ liệu: "
                    f"{type(error).__name__}. "
                    "Kiểm tra AWS credentials và API URL."
                }
            )

    def log_message(self, format, *args):
        pass


# ==========================================
# CHAY GIAO DIEN CUC BO
# ==========================================

if __name__ == "__main__":
    print("CV Recruitment Dashboard")
    print("http://127.0.0.1:5500")

    HTTPServer(
        ("127.0.0.1", 5500),
        Handler
    ).serve_forever()
