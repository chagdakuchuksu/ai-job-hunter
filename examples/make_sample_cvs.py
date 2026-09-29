"""Generate fictional sample CVs (PDF) for trying out AI Job Hunter.

Run from the project root:
    python examples/make_sample_cvs.py

Creates three CVs with different expected fit for examples/sample_job.txt:
    cv_strong_match.pdf   backend / AI-focused SE student
    cv_partial_match.pdf  frontend-focused developer
    cv_low_match.pdf      non-technical marketing profile
All people, companies and contact details are made up.
"""

from pathlib import Path

import pymupdf

OUT_DIR = Path(__file__).resolve().parent

CSS = """
* { font-family: sans-serif; }
body { font-size: 9.5pt; color: #222; line-height: 1.35; }
h1 { font-size: 20pt; margin: 0; color: #1a3d8f; }
.contact { color: #555; margin: 2pt 0 8pt 0; }
h2 { font-size: 11pt; color: #1a3d8f; border-bottom: 1px solid #1a3d8f;
     margin: 10pt 0 4pt 0; padding-bottom: 1pt; }
.role { font-weight: bold; margin: 5pt 0 0 0; }
.meta { color: #666; font-style: italic; margin: 0 0 2pt 0; }
ul { margin: 2pt 0 0 14pt; padding: 0; }
li { margin-bottom: 1.5pt; }
p { margin: 2pt 0; }
"""


def section(title: str, body: str) -> str:
    return f"<h2>{title}</h2>{body}"


def entry(role: str, meta: str, bullets: list[str]) -> str:
    items = "".join(f"<li>{b}</li>" for b in bullets)
    return f"<p class='role'>{role}</p><p class='meta'>{meta}</p><ul>{items}</ul>"


def build_pdf(filename: str, html: str) -> None:
    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842)  # A4
    page.insert_htmlbox(pymupdf.Rect(45, 40, 550, 810), html, css=CSS)
    doc.set_metadata({"title": filename, "author": "AI Job Hunter sample (fictional)"})
    doc.save(OUT_DIR / filename)
    doc.close()
    print(f"created {OUT_DIR / filename}")


STRONG = (
    "<h1>Maya Petrova</h1>"
    "<p class='contact'>Software Engineering Student &middot; maya.petrova@example.com &middot; "
    "github.com/maya-example &middot; Berlin</p>"
    + section("Summary", "<p>Third-year Software Engineering student focused on backend "
              "development and applied machine learning. Enjoys building clean, well-tested "
              "Python APIs and experimenting with LLM-powered tools.</p>")
    + section("Education", entry(
        "BSc Software Engineering, Example Technical University",
        "2023 &ndash; 2027 (expected) &middot; GPA 1.7",
        ["Coursework: Data Structures, Algorithms, Databases (SQL, PostgreSQL), Operating Systems (Linux), "
         "Object-Oriented Programming, Machine Learning, Natural Language Processing"]))
    + section("Experience", entry(
        "Software Engineering Intern &ndash; Nordlicht Analytics (fictional)", "Jun 2025 &ndash; Sep 2025",
        ["Built REST APIs with FastAPI and PostgreSQL serving model predictions to internal dashboards.",
         "Containerized services with Docker and added a GitHub Actions CI/CD pipeline running pytest.",
         "Reduced API response time by 40% by adding query indexes and caching."])
        + entry("Teaching Assistant &ndash; Algorithms &amp; Data Structures", "Oct 2024 &ndash; present",
                ["Run weekly tutorials for 40 students; review Python and Java assignments."]))
    + section("Projects", entry(
        "JobFit &ndash; LLM-assisted CV reviewer", "Python, FastAPI, OpenAI API, sentence-transformers",
        ["Compared CVs with job ads using embeddings and generated feedback with an LLM.",
         "Wrote unit tests with pytest; deployed with Docker on a Linux VM."])
        + entry("Sentiment classifier for product reviews", "PyTorch, scikit-learn, Pandas, NumPy",
                ["Fine-tuned a small transformer (NLP) model; 91% accuracy on a held-out test set."]))
    + section("Skills", "<p><b>Languages:</b> Python, Java, SQL, C++<br>"
              "<b>Backend:</b> FastAPI, Flask, REST APIs, PostgreSQL, Docker, Git, GitHub, CI/CD, Linux<br>"
              "<b>AI/ML:</b> machine learning, PyTorch, scikit-learn, Pandas, NumPy, NLP, LLMs<br>"
              "<b>Practices:</b> testing (pytest), code reviews, Agile</p>")
)

PARTIAL = (
    "<h1>Daniel Okafor</h1>"
    "<p class='contact'>Junior Frontend Developer &middot; daniel.okafor@example.com &middot; "
    "portfolio.example.dev &middot; Amsterdam</p>"
    + section("Summary", "<p>Frontend developer with two years of experience building responsive "
              "web applications. Comfortable with modern JavaScript tooling and eager to grow "
              "into full-stack development.</p>")
    + section("Experience", entry(
        "Frontend Developer &ndash; Brightpixel Studio (fictional)", "2024 &ndash; present",
        ["Build customer-facing web apps with TypeScript, React and Tailwind CSS.",
         "Integrate REST APIs from the backend team and write component tests with Jest.",
         "Maintain the design system and review pull requests on GitHub."])
        + entry("Web Development Intern &ndash; Localweb (fictional)", "2023",
                ["Built marketing pages with JavaScript, HTML and CSS; improved Lighthouse score to 95."]))
    + section("Education", entry(
        "BSc Information Systems, Example University of Applied Sciences", "2020 &ndash; 2024",
        ["Coursework: Web Development, Databases (SQL), Software Design"]))
    + section("Projects", entry(
        "Recipe finder", "JavaScript, Python (Flask backend)",
        ["Small full-stack app: Flask API with SQLite and a vanilla JavaScript frontend."]))
    + section("Skills", "<p><b>Frontend:</b> JavaScript, TypeScript, React, HTML, CSS, Figma<br>"
              "<b>Other:</b> Git, GitHub, REST APIs, SQL, basic Python</p>")
)

LOW = (
    "<h1>Sofia Lindqvist</h1>"
    "<p class='contact'>Marketing Coordinator &middot; sofia.lindqvist@example.com &middot; Stockholm</p>"
    + section("Summary", "<p>Creative marketing coordinator with four years of experience in "
              "social media campaigns, brand storytelling and event planning.</p>")
    + section("Experience", entry(
        "Marketing Coordinator &ndash; Fjord Coffee Co. (fictional)", "2022 &ndash; present",
        ["Plan and run social media campaigns on Instagram and TikTok; grew followers by 60%.",
         "Coordinate product launch events with up to 300 guests.",
         "Write newsletters and blog posts; manage the content calendar."])
        + entry("Communications Assistant &ndash; City Arts Festival (fictional)", "2020 &ndash; 2022",
                ["Handled press releases, sponsor communication and volunteer scheduling."]))
    + section("Education", entry(
        "BA Media and Communication, Example University",
        "2017 &ndash; 2020",
        ["Thesis on brand storytelling"]))
    + section("Skills", "<p>Copywriting, social media strategy, Canva, Adobe Photoshop, "
              "Google Analytics, event planning, Excel, public speaking</p>")
)


if __name__ == "__main__":
    build_pdf("cv_strong_match.pdf", STRONG)
    build_pdf("cv_partial_match.pdf", PARTIAL)
    build_pdf("cv_low_match.pdf", LOW)
