from app.services.matching_service import match_skills
from app.services.skill_service import extract_skills


def test_high_match():
    result = match_skills(
        cv_skills=["Python", "FastAPI", "SQL", "Docker", "Git"],
        job_skills=["Python", "FastAPI", "SQL", "Docker"],
    )
    assert result.match_percentage == 100
    assert result.missing_skills == []
    assert result.additional_skills == ["Git"]


def test_low_match():
    result = match_skills(
        cv_skills=["Java"],
        job_skills=["Python", "PyTorch", "NLP", "Docker"],
    )
    assert result.match_percentage == 0
    assert result.matched_skills == []
    assert result.missing_skills == ["Docker", "NLP", "Python", "PyTorch"]


def test_partial_match_rounds_percentage():
    result = match_skills(
        cv_skills=["Python", "Git"],
        job_skills=["Python", "Git", "Docker"],
    )
    assert result.match_percentage == 67  # 2 / 3
    assert result.matched_skills == ["Git", "Python"]
    assert result.missing_skills == ["Docker"]
    assert "2 of 3" in result.explanation


def test_no_skills_detected_in_job():
    result = match_skills(cv_skills=["Python"], job_skills=[])
    assert result.match_percentage is None
    assert result.additional_skills == ["Python"]
    assert "cannot be calculated" in result.explanation


def test_no_skills_anywhere():
    result = match_skills(cv_skills=[], job_skills=[])
    assert result.match_percentage is None
    assert result.matched_skills == result.missing_skills == []


def test_duplicates_are_ignored():
    result = match_skills(["Python", "Python"], ["Python", "Python", "SQL"])
    assert result.match_percentage == 50


def test_match_endpoint(client):
    response = client.post(
        "/api/skills/match",
        json={
            "cv_text": "Student with Python, Git and Linux experience.",
            "job_description": "We need Python, Docker and Git for a backend role.",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["match_percentage"] == 67
    assert body["matched_skills"] == ["Git", "Python"]
    assert body["missing_skills"] == ["Docker"]
    assert body["additional_skills"] == ["Linux"]


def test_match_endpoint_requires_cv_text(client):
    response = client.post(
        "/api/skills/match",
        json={"cv_text": "  ", "job_description": "We need Python, Docker and Git."},
    )
    assert response.status_code == 422


# --- Missing skills and score calculation ---------------------------------

CLOUD_JOB = (
    "Cloud engineer: build distributed systems and microservices in Go and Java "
    "on AWS with Kubernetes, Terraform, Kafka, Redis and PostgreSQL. "
    "CI/CD with GitHub Actions; monitoring with Prometheus and Grafana."
)


def test_every_job_skill_is_either_matched_or_missing():
    cv_skills = extract_skills("Python, Java, Docker, PostgreSQL, Git, AWS")
    job_skills = extract_skills(CLOUD_JOB)
    result = match_skills(cv_skills, job_skills)
    assert set(result.matched_skills) | set(result.missing_skills) == set(job_skills)
    assert not set(result.matched_skills) & set(result.missing_skills)
    assert result.matched_skills == ["AWS", "Java", "PostgreSQL"]
    for skill in ["Go", "Kafka", "Kubernetes", "Terraform", "Redis", "Grafana", "GitHub Actions"]:
        assert skill in result.missing_skills
    # CV-only skills never count as missing and don't change the score.
    assert "Python" in result.additional_skills


def test_score_is_matched_over_recognized_job_skills():
    job_skills = extract_skills(CLOUD_JOB)
    cv_skills = extract_skills("Java, AWS and PostgreSQL")
    result = match_skills(cv_skills, job_skills)
    assert result.match_percentage == round(100 * 3 / len(job_skills))
    assert f"3 of {len(job_skills)}" in result.explanation


def test_score_ignores_extra_cv_skills():
    base = match_skills(["Go"], ["Go", "Kafka"])
    extra = match_skills(["Go", "Python", "React", "Rust"], ["Go", "Kafka"])
    assert base.match_percentage == extra.match_percentage == 50
