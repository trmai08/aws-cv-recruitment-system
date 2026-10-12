import json
import re

def skill_exists(text, skill):
    pattern = r'(?<!\w)' + re.escape(skill.lower()) + r'(?!\w)'
    return re.search(pattern, text.lower()) is not None


def extract_experience(text):
    text = text.lower()

    years = 0
    months = 0

    year_match = re.search(
        r'(?:total\s+experience\s*:\s*)?(\d+(?:\.\d+)?)\s*\+?\s*years?',
        text
    )

    month_match = re.search(
        r'(?:total\s+experience\s*:\s*)?(\d+)\s*\+?\s*months?',
        text
    )

    if year_match:
        years = float(year_match.group(1))

    if month_match:
        months = int(month_match.group(1))

    return years + months / 12


def lambda_handler(event, context):

    text = event.get("text", "").lower()

    # Job mẫu
    job_title = "Java Backend Developer"

    required_skills = [
        "java",
        "spring boot",
        "sql",
        "rest api",
        "git"
    ]

    required_experience = 2.0

    matched_skills = []
    missing_skills = []

    for skill in required_skills:
        if skill_exists(text, skill):
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    # 1. Điểm kỹ năng: tối đa 70
    skill_score = (
        len(matched_skills) / len(required_skills)
    ) * 70

    # 2. Lấy kinh nghiệm
    experience = extract_experience(text)

    # 3. Điểm kinh nghiệm: tối đa 30
    experience_score = min(
        experience / required_experience,
        1
    ) * 30
    # 4. Tổng điểm
    total_score = skill_score + experience_score

    skill_score = round(skill_score, 2)
    experience_score = round(experience_score, 2)
    total_score = round(total_score, 2)
    experience = round(experience, 2)

    print("Job:", job_title)
    print("Matched skills:", matched_skills)
    print("Missing skills:", missing_skills)
    print("Experience:", experience)
    print("Skill score:", skill_score)
    print("Experience score:", experience_score)
    print("Total score:", total_score)

    return {
        "statusCode": 200,
        "body": {
            "jobTitle": job_title,
            "matchedSkills": matched_skills,
            "missingSkills": missing_skills,
            "experienceYears": experience,
            "skillScore": skill_score,
            "experienceScore": experience_score,
            "totalScore": total_score
        }
    }