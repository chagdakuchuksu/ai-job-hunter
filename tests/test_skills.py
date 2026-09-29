import pytest

from app.services.skill_service import extract_skills, load_skill_dictionary


def test_dictionary_contains_core_skills():
    skills = load_skill_dictionary()
    for name in ["Python", "FastAPI", "Machine Learning", "NLP", "CI/CD", "C++"]:
        assert name in skills


def test_detects_case_insensitive_names():
    assert extract_skills("experience with PYTHON and fastapi") == ["FastAPI", "Python"]


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Background in ML", "Machine Learning"),
        ("natural language processing projects", "NLP"),
        ("worked with large language models", "LLM"),
        ("deployed on k8s", "Kubernetes"),
        ("used sklearn", "scikit-learn"),
        ("object-oriented design", "OOP"),
        ("Postgres database", "PostgreSQL"),
        ("built RESTful services", "REST APIs"),
        ("pipelines in GitHub Actions", "GitHub Actions"),
        ("wrote tests with pytest", "Testing"),
    ],
)
def test_normalizes_variants(text, expected):
    assert expected in extract_skills(text)


def test_does_not_match_inside_other_words():
    skills = extract_skills("JavaScript and PostgreSQL and C#")
    assert "Java" not in skills
    assert "SQL" not in skills
    assert "C" not in skills
    assert {"JavaScript", "PostgreSQL"} <= set(skills)


def test_c_and_cpp_are_distinguished():
    assert extract_skills("C/C++ programming") == ["C", "C++"]
    assert extract_skills("C++ only") == ["C++"]


def test_case_sensitive_aliases_ignore_ordinary_words():
    # "rest", "go", "react" and "c" as ordinary lowercase words are not skills.
    assert extract_skills("take a rest, then go and react to feedback, plan c") == []


def test_git_and_github_are_separate():
    assert extract_skills("GitHub profile") == ["GitHub"]
    assert extract_skills("Git and GitHub") == ["Git", "GitHub"]


def test_no_skills_in_unrelated_text():
    assert extract_skills("I enjoy hiking and cooking.") == []


def test_cv_upload_returns_skills(client, pdf_factory):
    pdf = pdf_factory("Skills: Python, Docker, machine learning")
    response = client.post(
        "/api/cv/upload", files={"file": ("cv.pdf", pdf, "application/pdf")}
    )
    assert response.status_code == 200
    assert response.json()["skills"] == ["Docker", "Machine Learning", "Python"]


def test_job_endpoint_returns_skills(client):
    response = client.post(
        "/api/job/analyze",
        json={"description": "Looking for a backend engineer with Python and SQL."},
    )
    assert response.json()["skills"] == ["Python", "SQL"]


# --- Token-aware matching ------------------------------------------------


@pytest.mark.parametrize(
    "text, present, absent",
    [
        ("Frontend work in JavaScript", {"JavaScript"}, {"Java"}),
        ("Backend in Java", {"Java"}, {"JavaScript"}),
        ("Java and JavaScript", {"Java", "JavaScript"}, set()),
        ("Java/JavaScript developer", {"Java", "JavaScript"}, set()),
    ],
)
def test_java_vs_javascript(text, present, absent):
    skills = set(extract_skills(text))
    assert present <= skills
    assert not (absent & skills)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Modern C++ (C++17)", ["C++"]),
        ("Embedded C", ["C"]),
        ("C, C++ and C#", ["C", "C#", "C++"]),
        ("C/C++ programming", ["C", "C++"]),
        ("reports to C-level executives", []),
    ],
)
def test_c_family(text, expected):
    assert extract_skills(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "Services written in Go",
        "Go, Rust or Java",
        "Experience with Golang",
        "backend (Go) microservices",
    ],
)
def test_go_is_detected(text):
    assert "Go" in extract_skills(text)


@pytest.mark.parametrize(
    "text",
    [
        "good communication skills",
        "we are going to grow",
        "ready to go live",
        "our go-to-market team",
        "Google Docs and MongoDB",
        "Go-to-market strategy",
    ],
)
def test_go_is_not_matched_in_normal_words(text):
    assert "Go" not in extract_skills(text)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("deployed on k8s", "Kubernetes"),
        ("backend in golang", "Go"),
        ("frontend in ts", "TypeScript"),
        ("some js experience", "JavaScript"),
        ("fast cpp code", "C++"),
        ("postgres tuning", "PostgreSQL"),
        ("ml pipelines", "Machine Learning"),
        ("Amazon Web Services", "AWS"),
        ("Google Cloud Platform", "GCP"),
        ("Spring Boot services", "Spring Boot"),
        ("microservice architecture", "Microservices"),
        ("event streaming with Apache Kafka", "Kafka"),
        ("dashboards in Grafana with Prometheus", "Prometheus"),
        ("APIs with gRPC and GraphQL", "gRPC"),
        ("NoSQL stores such as DynamoDB", "DynamoDB"),
    ],
)
def test_aliases(text, expected):
    assert expected in extract_skills(text)


def test_alias_inside_other_token_does_not_match():
    skills = extract_skills("Node.js, HTML, NoSQL, PostgreSQL, Kotlin")
    assert "Node.js" in skills and "NoSQL" in skills
    assert not {"JavaScript", "Machine Learning", "SQL"} & set(skills)
