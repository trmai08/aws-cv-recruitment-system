
import boto3
import json
import re
from urllib.parse import unquote_plus

textract = boto3.client("textract")

# ============================================
# 1. DANH SACH KY NANG
# ============================================

SKILLS = [
    "java", "spring boot", "python",
    "javascript", "react", "angular",
    "sql", "mysql", "sql server",
    "postgresql", "mongodb", "docker",
    "kubernetes", "aws", "git",
    "rest api", "microservices",
    "html", "css", "c#", ".net",
    "spring mvc", "spring security",
    "jpa", "hibernate", "maven",
    "thymeleaf", "postman"
]

SKILL_ALIASES = {
    "rest api": [
        "rest api", "rest apis",
        "restful api", "restful apis"
    ],
    "git": ["git", "github"],
    "jpa": ["jpa"],
    "hibernate": ["hibernate"],
    "aws": ["aws", "amazon web services"]
}

SECTION_HEADINGS = [
    "professional summary",
    "profile",
    "education",
    "technical skills",
    "skills",
    "work experience",
    "experience",
    "projects",
    "soft skills",
    "contact",
    "languages",
    "foreign language",
    "summary",
    "học vấn",
    "kinh nghiệm",
    "kỹ năng"
]


# ============================================
# 2. CAC HAM HO TRO
# ============================================

def normalize_spaces(value):
    return re.sub(r"\s+", " ", str(value)).strip()


def is_heading(line):
    value = normalize_spaces(line).lower()
    return value in SECTION_HEADINGS


# ============================================
# 3. TRICH XUAT HO TEN
# ============================================

def extract_name(lines):

    for line in lines[:12]:
        match = re.match(
            r"^(?:full name|name|họ và tên)"
            r"\s*:\s*(.+)$",
            line,
            re.IGNORECASE
        )

        if match:
            return normalize_spaces(match.group(1))

    parts = []

    for line in lines[:6]:

        value = normalize_spaces(line)

        if is_heading(value):
            break

        if re.search(
            r"@|https?://|\d|developer|engineer"
            r"|intern|position|summary",
            value,
            re.IGNORECASE
        ):
            break

        words = value.split()

        if (
            1 <= len(words) <= 4
            and len(value) <= 45
            and re.fullmatch(
                r"[A-Za-zÀ-ỹ\s'-]+",
                value
            )
        ):
            parts.append(value)

            if len(" ".join(parts).split()) >= 3:
                break
        else:
            break

    return normalize_spaces(" ".join(parts))


# ============================================
# 4. TRICH XUAT EMAIL
# ============================================

def extract_email(text):

    match = re.search(
        r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
        text
    )

    return match.group(0) if match else ""


# ============================================
# 5. TRICH XUAT SO DIEN THOAI
# ============================================

def extract_phone(lines):

    pattern = (
        r"(?<!\d)(?:\+84|0)"
        r"(?:[\s.-]?\d){9}(?!\d)"
    )

    def find_phone(text):

        for match in re.finditer(pattern, text):

            digits = re.sub(
                r"\D", "", match.group()
            )

            if digits.startswith("84"):
                digits = "0" + digits[2:]

            if (
                len(digits) == 10
                and re.fullmatch(
                    r"0[35789]\d{8}", digits
                )
            ):
                return digits

        return ""

    for i, line in enumerate(lines):

        if re.search(
            r"phone|mobile|điện thoại",
            line,
            re.IGNORECASE
        ):

            for candidate in lines[i:i + 4]:

                found = find_phone(candidate)

                if found:
                    return found

    for line in lines:

        found = find_phone(line)

        if found:
            return found

    return ""


# ============================================
# 6. TRICH XUAT KY NANG
# ============================================

def extract_skills(text):

    detected = []
    lower_text = text.lower()

    for skill in SKILLS:

        aliases = SKILL_ALIASES.get(
            skill, [skill]
        )

        for alias in aliases:

            pattern = (
                r"(?<!\w)"
                + re.escape(alias)
                + r"(?!\w)"
            )

            if re.search(pattern, lower_text):
                detected.append(skill)
                break

    return sorted(set(detected))


# ============================================
# 7. TRICH XUAT KINH NGHIEM
# ============================================

def extract_experience(lines):

    text = "\n".join(lines)

    number = r"\d+(?:[.,]\d+)?"
    year_unit = r"(?:years?|yrs?|năm)"
    month_unit = r"(?:months?|mos?|tháng)"

    def to_years(match):

        years = 0.0

        if match.group("years"):
            years = float(
                match.group("years").replace(",", ".")
            )

        months = 0.0

        if match.group("months"):
            months = float(
                match.group("months").replace(",", ".")
            )

        return round(years + months / 12, 2)

    # Truong hop co tong kinh nghiem
    total_pattern = (
        r"(?:total experience|tổng kinh nghiệm|"
        r"kinh nghiệm)\s*:\s*"
        + rf"(?:(?P<years>{number})\s*{year_unit}\s*)?"
        + rf"(?:(?P<months>{number})\s*{month_unit})?"
    )

    match = re.search(
        total_pattern,
        text,
        re.IGNORECASE
    )

    if match and (
        match.group("years")
        or match.group("months")
    ):
        return (
            match.group(0).strip(),
            to_years(match)
        )

    # Vi du: 2 years 6 months of experience
    english_pattern = (
        rf"(?:(?P<years>{number})\s*{year_unit}\s*)?"
        + rf"(?:(?P<months>{number})\s*{month_unit})?"
        + r"\s+(?:of\s+)?"
        r"(?:practical\s+)?experience\b"
    )

    match = re.search(
        english_pattern,
        text,
        re.IGNORECASE
    )

    if match and (
        match.group("years")
        or match.group("months")
    ):
        return (
            match.group(0).strip(),
            to_years(match)
        )

    return "", None


# ============================================
# 8. TONG HOP THONG TIN UNG VIEN
# ============================================

def extract_information(lines):

    lines = [
        normalize_spaces(line)
        for line in lines
        if normalize_spaces(line)
    ]

    text = "\n".join(lines)

    name = extract_name(lines)
    email = extract_email(text)
    phone = extract_phone(lines)
    skills = extract_skills(text)

    experience, experience_years = (
        extract_experience(lines)
    )

    warnings = []

    if not name:
        warnings.append(
            "Không nhận diện được họ tên"
        )

    if not email:
        warnings.append(
            "Không tìm thấy email"
        )

    if not phone:
        warnings.append(
            "Không tìm thấy số điện thoại"
        )

    if not skills:
        warnings.append(
            "Không nhận diện được kỹ năng"
        )

    if experience_years is None:
        warnings.append(
            "Chưa xác định được số năm kinh nghiệm"
        )

    status = (
        "COMPLETE"
        if not warnings
        else "PARTIAL"
    )

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "experience": experience,
        "experienceYears": experience_years,
        "warnings": warnings,
        "extractionStatus": status
    }


# ============================================
# 9. XAC DINH JOB ID TU DUONG DAN S3
# ============================================

def extract_job_id(key):

    parts = key.split("/")

    if (
        len(parts) >= 3
        and parts[0] == "cvs"
        and parts[1]
    ):
        return parts[1]

    return None


# ============================================
# 10. XU LY CV BANG TEXTRACT
# ============================================

def process_cv(bucket, key):

    if not key.lower().endswith(".pdf"):

        return {
            "statusCode": 400,
            "error": "Only PDF is supported",
            "file": key
        }

    response = textract.detect_document_text(
        Document={
            "S3Object": {
                "Bucket": bucket,
                "Name": key
            }
        }
    )

    lines = [
        block["Text"]
        for block in response["Blocks"]
        if block["BlockType"] == "LINE"
    ]

    candidate = extract_information(lines)

    return {
        "statusCode": 200,
        "bucket": bucket,
        "key": key,
        "file": key,
        "jobId": extract_job_id(key),
        "candidate": candidate
    }


# ============================================
# 11. LAMBDA HANDLER
# ============================================

def lambda_handler(event, context):

    try:

        # Xu ly su kien tu S3
        if "Records" in event:

            results = []

            for record in event["Records"]:

                bucket = record["s3"]["bucket"]["name"]

                key = unquote_plus(
                    record["s3"]["object"]["key"]
                )

                results.append(
                    process_cv(bucket, key)
                )

            # Chi ghi trang thai, khong in noi dung CV
            for result in results:

                print(json.dumps({
                    "file": result.get("file"),
                    "statusCode": result.get(
                        "statusCode"
                    ),
                    "extractionStatus": (
                        result.get("candidate", {})
                        .get("extractionStatus")
                    )
                }, ensure_ascii=False))

            return {"results": results}

        # Xu ly Test Event thu cong
        bucket = event["bucket"]
        key = event["key"]

        return process_cv(bucket, key)

    except Exception as error:

        print(
            "CV_PROCESS_ERROR:",
            type(error).__name__
        )

        raise
