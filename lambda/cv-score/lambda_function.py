import boto3
import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal

lambda_client = boto3.client("lambda")
table = boto3.resource("dynamodb").Table("CVApplications")
SOURCE_LAMBDA = "cv-process"
BUCKET = "cv-recruitment-ute-2026-2027"


def to_json(value):
    return json.loads(json.dumps(value, default=lambda x: float(x) if isinstance(x, Decimal) else str(x)))


def reply(code, data):
    return {"statusCode": code, "headers": {"Content-Type": "application/json"},
            "body": json.dumps(to_json(data), ensure_ascii=False)}


def score_cv(candidate, required, minimum):
    skills = {str(s).strip().lower() for s in candidate.get("skills", []) if str(s).strip()}
    wanted = {str(s).strip().lower() for s in required if str(s).strip()}
    if not wanted:
        raise ValueError("requiredSkills must not be empty")
    if minimum <= 0:
        raise ValueError("minExperience must be greater than 0")
    matched = sorted(skills & wanted)
    missing = sorted(wanted - skills)
    skill_score = round(len(matched) / len(wanted) * 100, 2)
    exp_raw = candidate.get("experienceYears")
    exp_years = float(exp_raw) if exp_raw is not None else None
    exp_score = round(min(max(exp_years or 0, 0) / minimum, 1) * 100, 2)
    total = round(skill_score * 0.7 + exp_score * 0.3, 2)
    warnings = list(candidate.get("warnings") or [])
    if exp_years is None and not any("kinh nghiệm" in str(w).lower() for w in warnings):
        warnings.append("Chưa xác định được số năm kinh nghiệm")
    status = "PARTIAL" if warnings or candidate.get("extractionStatus") == "PARTIAL" else "COMPLETE"
    return {"matchedSkills": matched, "missingSkills": missing,
            "skillScore": skill_score, "experienceScore": exp_score,
            "totalScore": total, "experienceYears": exp_years,
            "warnings": warnings, "extractionStatus": status}


def load_candidate(payload):
    if isinstance(payload.get("candidate"), dict):
        return payload["candidate"]
    key = payload.get("key", "")
    bucket = payload.get("bucket", BUCKET)
    if bucket != BUCKET or not key.startswith("cvs/") or not key.lower().endswith(".pdf"):
        raise ValueError("bucket/key must point to a PDF under cvs/ in the project bucket")
    response = lambda_client.invoke(FunctionName=SOURCE_LAMBDA,
                                    InvocationType="RequestResponse",
                                    Payload=json.dumps({"bucket": bucket, "key": key}).encode("utf-8"))
    result = json.loads(response["Payload"].read())
    if response.get("FunctionError") or result.get("statusCode") != 200 or "candidate" not in result:
        raise RuntimeError("cv-process failed: " + str(result.get("error", "unknown")))
    return result["candidate"]


def process(payload):
    required = payload.get("requiredSkills", ["java", "spring boot", "sql", "git"])
    if not isinstance(required, list):
        raise ValueError("requiredSkills must be an array")
    minimum = float(payload.get("minExperience", 2))
    job_id = str(payload.get("jobId", "java-backend"))
    candidate = load_candidate(payload)
    scores = score_cv(candidate, required, minimum)
    key = str(payload.get("key", "manual"))
    candidate_id = payload.get("candidateId") or hashlib.sha256(
        f"{job_id}|{key}|{candidate.get('email','')}|{candidate.get('name','')}".encode()
    ).hexdigest()[:20]
    item = {"candidateId": candidate_id, "jobId": job_id,
            "name": candidate.get("name", ""), "email": candidate.get("email", ""),
            "phone": candidate.get("phone", ""), "cvKey": key,
            "skills": candidate.get("skills", []),
            "requiredSkills": required, **scores,
            "scoredAt": datetime.now(timezone.utc).isoformat()}
    # DynamoDB không nhận float trực tiếp: chuyển mọi số sang Decimal.
    db_item = json.loads(json.dumps(item, ensure_ascii=False), parse_float=Decimal)
    table.put_item(Item=db_item)
    print(json.dumps({"candidateId": candidate_id, "jobId": job_id,
                      "extractionStatus": scores["extractionStatus"], "saved": True}))
    return to_json(item)


def lambda_handler(event, context):
    try:
        http = event.get("requestContext", {}).get("http", {})
        method = http.get("method", event.get("httpMethod", ""))
        path = event.get("rawPath", event.get("path", ""))
        if method == "GET" and path.endswith("/candidates"):
            # Demo: scan tối đa 100 bản ghi; production nên dùng phân trang.
            items = table.scan(Limit=100).get("Items", [])
            return reply(200, {"count": len(items), "items": items})
        if method == "POST" and path.endswith("/candidates"):
            payload = json.loads(event.get("body") or "{}")
            return reply(200, process(payload))
        if method:
            return reply(404, {"error": "Route not found"})
        return process(event)  # Test Event trực tiếp trong Lambda Console
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        return reply(400, {"error": str(exc)})
    except Exception as exc:
        print("CV_SCORE_ERROR:", type(exc).__name__)
        return reply(500, {"error": type(exc).__name__, "message": "Processing failed; see CloudWatch logs"})
