
import boto3
import json
import re
from urllib.parse import unquote_plus

textract = boto3.client("textract")

SKILLS = [
    "python", "java", "spring boot", "sql",
    "mysql", "aws", "lambda", "s3",
    "dynamodb", "html", "css", "javascript",
    "react", "docker", "git"
]

def extract_information(text):
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    email_match = re.search(
        r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
        text
    )

    name = ""
    for i, line in enumerate(lines):
        match = re.match(
            r"^(?:Họ và tên|Full Name|Name)\s*:\s*(.+)$",
            line,
            re.IGNORECASE
        )
        if match:
            name = match.group(1).strip()
            break

    if not name and lines:
        name_parts = []
        for line in lines[:3]:
            if re.fullmatch(
                r"[A-Za-zÀ-ỹ]+(?:\s+[A-Za-zÀ-ỹ]+)*",
                line
            ):
                name_parts.append(line)
            else:
                break

        name = " ".join(name_parts)

    phone = ""
    for i, line in enumerate(lines):
        if re.search(
            r"(?:Số điện thoại|Phone|Mobile|Điện thoại)",
            line,
            re.IGNORECASE
        ):
            candidates = [line]
            candidates.extend(lines[i + 1:i + 5])

            for candidate in candidates:
                for match in re.finditer(
                    r"(?<!\d)(?:\+84|0)[\d\s.-]{8,16}(?!\d)",
                    candidate
                ):
                    digits = re.sub(
                        r"\D", "", match.group()
                    )

                    if digits.startswith("84"):
                        digits = "0" + digits[2:]

                    if (
                        len(digits) == 10
                        and digits.startswith("0")
                    ):
                        phone = digits
                        break

                if phone:
                    break

        if phone:
            break

    if not phone:
        for match in re.finditer(
            r"(?<!\d)0[35789](?:[\s.-]?\d){8}(?!\d)",
            text
        ):
            digits = re.sub(r"\D", "", match.group())
            if len(digits) == 10:
                phone = digits
                break

    skills = [
        skill for skill in SKILLS
        if re.search(
            r"(?<!\w)" + re.escape(skill) + r"(?!\w)",
            text,
            re.IGNORECASE
        )
    ]

    experience_lines = []
    in_experience = False

    for line in lines:
        if re.match(
            r"^(Experience|Kinh nghiệm)$",
            line,
            re.IGNORECASE
        ):
            in_experience = True
            continue

        if in_experience:
            if re.match(
                r"^(Education|Soft Skills|Skills|"
                r"Foreign Language|Học vấn|Kỹ năng)$",
                line,
                re.IGNORECASE
            ):
                break

            experience_lines.append(line)

    experience = " ".join(experience_lines)

    return {
        "name": name,
        "email": (
            email_match.group(0)
            if email_match else ""
        ),
        "phone": phone,
        "skills": skills,
        "experience": experience,
        "raw_text": text
    }

def lambda_handler(event, context):
    if "Records" in event:
        record = event["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(
            record["s3"]["object"]["key"]
        )
    else:
        bucket = event["bucket"]
        key = event["key"]

    if not key.lower().endswith(".pdf"):
        return {
            "statusCode": 400,
            "error": "Only PDF files are supported"
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

    text = "\n".join(lines)
    candidate = extract_information(text)

    result = {
        "statusCode": 200,
        "bucket": bucket,
        "file": key,
        "candidate": candidate
    }

    print(json.dumps(result, ensure_ascii=False))
    return result
