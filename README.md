---
title: AI Job Hunter
emoji: 🎯
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8080
pinned: false
license: mit
short_description: Compare a CV with a job post (skills + similarity)
---

# AI Job Hunter

[![Live Demo](https://img.shields.io/badge/Live-Demo-success)](https://ai-job-hunter-734011782496.europe-west1.run.app/)

Upload your CV (PDF), paste a job description, and get a transparent breakdown of how the two relate:

- **Skill match:** which skills from the job posting appear in your CV, and which are missing
- **Semantic similarity:** how close the overall content of the two texts is, using sentence embeddings

> **Important:** every score in this project is a technical/demo metric for self-improvement.
> It is **not** a hiring prediction and must not be used for automated hiring decisions.

Built with **Python · FastAPI · PyMuPDF · sentence-transformers · vanilla HTML/CSS/JS**.

## Live Demo

**<https://ai-job-hunter-734011782496.europe-west1.run.app/>**

Try it in your browser without installing anything: upload a CV (PDF), paste a job
description and click **Analyze**. The demo runs the full app, including semantic similarity,
from the project's `Dockerfile` on Google Cloud Run. Interactive API docs are at
[`/docs`](https://ai-job-hunter-734011782496.europe-west1.run.app/docs).

Please don't upload a CV with personal details you wouldn't want to send to a public demo.
The fictional CVs in [`examples/`](examples) work well for trying it out.

---

## Problem statement

Students applying for internships often can't tell how well their CV covers a posting's
requirements, or which of the requested skills they are missing. Applicant tracking systems are opaque. This project
shows a *transparent* alternative. Every number comes with an explanation of how it was
calculated, and the deterministic skill match is kept separate from the ML-based similarity score.

## Features

- CV PDF upload with validation (type, magic bytes, size, page count, encrypted/corrupt/scanned PDFs)
- Text extraction with PyMuPDF; CVs are processed **in memory and never stored**
- Job description validation and normalization
- Skill extraction from a configurable dictionary (`app/data/skills.json`, 60 skills) with alias
  normalization (e.g. `ml` → Machine Learning, `golang` → Go, `k8s` → Kubernetes, `postgres` → PostgreSQL)
- Token-aware matching: `Java` ≠ `JavaScript`, `C` ≠ `C++`, and `Go` is not matched in "good", "going" or "go-to-market"
- Deterministic skill match score with matched / missing / additional skills
- Semantic similarity with a small local embedding model (`all-MiniLM-L6-v2`, runs on CPU)
- Clean JSON errors that never leak internal exception details
- Responsive single-page frontend with no framework and no build step
- 99 automated tests (98 run by default, offline, in about a second; the embedding model is mocked),
  run on every push by GitHub Actions

## Architecture

```
Browser (frontend/: HTML + CSS + vanilla JS)
   │  POST /api/analyze  (multipart: cv_file + job_description)
   ▼
FastAPI routers (app/api/)          ← thin: parse request, call services, shape response
   │
   ▼
analysis_service.run_analysis()     ← orchestrates the pipeline below
   ├── cv_service        PDF validation + PyMuPDF text extraction
   ├── job_service       job description validation + normalization
   ├── skill_service     dictionary-based skill extraction
   ├── matching_service  deterministic skill match score
   └── semantic_service  sentence-embedding cosine similarity
```

Each smaller endpoint (`/api/cv/upload`, `/api/job/analyze`, `/api/skills/match`) reuses the
same service functions, so no logic is duplicated between endpoints. No database is needed,
because nothing has to be persisted.

```
app/
├── main.py              app setup, CORS, routers, serves the frontend
├── config.py            settings from environment variables / .env
├── errors.py            AppError + JSON error handlers
├── api/                 routers: health, cv, job, skills, analysis
├── schemas/             Pydantic request/response models
├── services/            business logic (see diagram)
├── data/skills.json     editable skills dictionary
└── utils/text.py        text normalization helpers
frontend/                index.html, styles.css, app.js
examples/                sample CVs (PDF) + job descriptions for trying the app
tests/                   pytest suite
.github/workflows/       CI: runs pytest on every push
```

## Tech stack

| Area | Choice | Why |
|---|---|---|
| API | FastAPI + Uvicorn | typed request validation, automatic OpenAPI docs |
| PDF | PyMuPDF | fast, reliable text extraction, no external tools |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) | well-established, ~90 MB, runs on a laptop CPU |
| Frontend | HTML, CSS, vanilla JS | no build step; served by FastAPI |
| Tests | pytest + FastAPI TestClient | fast, with the embedding model mocked |

## How it works

1. **CV:** the PDF is read in chunks (oversized uploads are rejected early), checked for the `%PDF-` signature, opened with PyMuPDF, and its text is extracted and normalized.
2. **Job description:** whitespace and unicode are normalized; length is validated.
3. **Skills:** both texts are scanned for every skill alias in `skills.json`.
4. **Skill match:** the job's detected skills are compared with the CV's (see methodology below).
5. **Semantic similarity:** both texts are embedded and compared with cosine similarity.

## Installation

Requires **Python 3.10+** (developed on 3.14; CI uses 3.12).

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

pip install -r requirements-dev.txt   # app + test dependencies
cp .env.example .env                  # optional: only needed to change settings
```

`sentence-transformers` installs PyTorch. On Windows and macOS pip installs a CPU build by
default; on Linux the default build includes large CUDA libraries, so install the CPU build
first if you don't have a GPU:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

The embedding model itself (~90 MB) is downloaded from Hugging Face on the first analysis and
cached afterwards.

## Environment variables

All optional. See [.env.example](.env.example).

| Variable | Default | Purpose |
|---|---|---|
| `SEMANTIC_ENABLED` | `true` | Set `false` to skip embeddings |
| `PRELOAD_EMBEDDING_MODEL` | `false` | Load the embedding model at startup instead of on the first analysis (the Docker image sets it to `true`) |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Any sentence-transformers model name |
| `MAX_UPLOAD_MB` | `5` | Max CV file size |
| `MAX_PDF_PAGES` | `20` | Max CV pages |
| `MIN_JOB_CHARS` / `MAX_JOB_CHARS` | `30` / `20000` | Job description length limits |
| `CORS_ORIGINS` | `http://localhost:8000,http://127.0.0.1:8000` | Allowed origins for cross-origin API calls |

`.env` is git-ignored.

## How to run

There are two ways to use the app.

### Option 1: Live Demo (no installation)

Open **<https://ai-job-hunter-734011782496.europe-west1.run.app/>** in your browser, upload a
CV (PDF) and paste a job description. The same deployment also serves the interactive API docs
at <https://ai-job-hunter-734011782496.europe-west1.run.app/docs>.

The demo runs on Google Cloud Run, which can shut the app down when it isn't used. The first
request after a quiet period may then take a little longer while it starts again.

### Option 2: Run locally (for development)

After [installing](#installation) the dependencies, start the development server:

```bash
uvicorn app.main:app --reload
```

This runs a private copy of the app on your own machine only (not the public demo):

- Web app: <http://127.0.0.1:8000>
- Interactive API docs: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>

### Sample inputs

Try either option with one of the fictional sample CVs and one of the two job descriptions
(`sample_job.txt`: backend/AI intern; `sample_job_cloud.txt`: cloud & distributed systems engineer):

| CV | Profile | Backend/AI job: skills · semantic | Cloud job: skills · semantic |
|---|---|---|---|
| `examples/cv_strong_match.pdf` | backend/AI student | 100% · 74% | 38% · 67% |
| `examples/cv_partial_match.pdf` | frontend developer | 41% · 67% | 16% · 65% |
| `examples/cv_low_match.pdf` | marketing coordinator | 0% · 24% | 0% · 17% |

The cloud job is intentionally harder: it names 32 recognized skills (Go, Kafka, Kubernetes,
Terraform, gRPC, ...) and contains traps such as "go-to-market", "C-level" and "Node.js"
that must not be detected as Go, C or JavaScript.

`examples/sample_cv.pdf` is a minimal plain-text CV. Regenerate or edit the samples with `python examples/make_sample_cvs.py`.
The scores above were measured on a local run. After the server starts, the first analysis takes
longer (~10–30 s locally) while the embedding model loads; later ones take about a second.

## Deploying to Hugging Face Spaces

The repository is ready to run as a [Docker Space](https://huggingface.co/docs/hub/spaces-sdks-docker)
on the free **CPU basic** hardware, with semantic similarity enabled:

- The YAML block at the top of this README is the Space configuration (`sdk: docker`, `app_port: 8080`).
- `Dockerfile` installs the CPU-only PyTorch build and the app's dependencies, downloads
  `all-MiniLM-L6-v2` at build time (so it is part of the image), and starts Uvicorn on the port
  given in `$PORT`, falling back to 8080. The same image runs the Cloud Run live demo.
- The image sets `PRELOAD_EMBEDDING_MODEL=true`, so the model is loaded while the Space starts
  and the first analysis is fast.
- `.dockerignore` keeps local files, secrets, tests and examples out of the image.

To deploy, create a Space with the **Docker** SDK and upload the project with the `hf` CLI
(`pip install -U huggingface_hub`, then `hf auth login` with a token that has *write* access):

```bash
hf repos create <your-username>/ai-job-hunter --repo-type space --space-sdk docker --exist-ok
```

```bash
hf upload <your-username>/ai-job-hunter . . --repo-type space --exclude ".venv/*" --exclude ".git/*" --exclude ".claude/*" --exclude ".env" --exclude "*__pycache__*" --exclude ".pytest_cache/*"
```

The Space builds the image automatically and is then available at
`https://huggingface.co/spaces/<your-username>/ai-job-hunter`. Free Spaces go to sleep after a
period of inactivity and wake up on the next visit.

## API endpoints

| Method | Path | Input | Returns |
|---|---|---|---|
| GET | `/health` | none | `{"status": "ok"}` |
| POST | `/api/cv/upload` | multipart `file` (PDF) | extracted text, page/word counts, detected skills |
| POST | `/api/job/analyze` | JSON `{"description": "..."}` | normalized text, counts, detected skills |
| POST | `/api/skills/match` | JSON `{"cv_text": "...", "job_description": "..."}` | skill match only (no PDF needed) |
| POST | `/api/analyze` | multipart `cv_file` (PDF) + `job_description` | complete analysis |

Errors always return JSON: `{"detail": "<user-safe message>"}` with a suitable status code
(`413` too large, `415` not a PDF, `422` invalid input, `400` unreadable PDF, `500` generic).

### Example usage

Against a local server (for the live demo, replace `http://127.0.0.1:8000` with
`https://ai-job-hunter-734011782496.europe-west1.run.app`):

```bash
curl -F "cv_file=@examples/sample_cv.pdf" \
     -F "job_description=<examples/sample_job.txt" \
     http://127.0.0.1:8000/api/analyze
```

Response (shortened):

```json
{
  "cv":  { "filename": "sample_cv.pdf", "page_count": 1, "skills": ["Algorithms", "FastAPI", "Python", "..."], "...": "..." },
  "job": { "word_count": 91, "skills": ["CI/CD", "Docker", "FastAPI", "PostgreSQL", "Python", "..."], "...": "..." },
  "skill_match": {
    "match_percentage": 71,
    "matched_skills": ["Algorithms", "Data Structures", "FastAPI", "Flask", "Git", "GitHub", "Linux", "Machine Learning", "Python", "REST APIs", "SQL", "Testing"],
    "missing_skills": ["CI/CD", "Docker", "LLM", "NLP", "PostgreSQL"],
    "additional_skills": ["Java", "JavaScript", "OOP", "Pandas", "scikit-learn"],
    "explanation": "12 of 17 skills detected in the job description were also found in the CV."
  },
  "semantic_similarity": { "available": true, "score": 0.7187, "percentage": 72, "model": "all-MiniLM-L6-v2" },
  "disclaimer": "These results are technical indicators for self-improvement only. They are not a hiring prediction or an automated hiring decision."
}
```

## Matching methodology

The skill match is deliberately simple and fully deterministic:

```
match_percentage = round(100 × |job skills ∩ CV skills| / |job skills|)
```

- **Job skills:** known skills detected in the job description
- **Matched:** job skills also detected in the CV
- **Missing:** every recognized job skill not detected in the CV (so matched + missing = all job skills)
- **Additional:** CV skills the job description doesn't mention (they don't affect the score)
- If no known skills are detected in the job description, the score is `null` rather than a misleading 0% or 100%.

**Skill detection** uses case-insensitive whole-token matching of each alias in
`app/data/skills.json`. Three rules keep false positives down:
- **Token boundaries:** letters, digits, `+`, `#` (and a leading `.`) count as part of a token, so
  `Java` doesn't match inside `JavaScript`, `C` doesn't match `C++`/`C#`, `SQL` doesn't match
  `PostgreSQL`, `Go` doesn't match `good`/`Google`, and `js` doesn't match inside `Node.js`.
- **Case-sensitive aliases:** the few aliases that are also everyday English words
  (`C`, `Go`, `REST`, `CI`, `React`) are listed in `case_sensitive_aliases` and must match exactly,
  so "go home" or "take a rest" are ignored.
- **Short aliases before a hyphen:** `C`, `Go` and `CI` are not matched in phrases like
  "C-level" or "go-to-market".

To add a skill, add an entry to `skills.json`. No code changes are needed.

## Semantic similarity

The skill match only sees exact keywords. Semantic similarity instead captures whether the
texts are *about* similar things: "built web services in Python" is close to "backend API
development" even without shared keywords.

- Model: `all-MiniLM-L6-v2` (sentence-transformers), 384-dim embeddings, runs locally on CPU.
- The model reads ~256 tokens at a time, so each text is split into 150-word chunks. The chunk embeddings are averaged into one normalized vector per document.
- **score** = cosine similarity of the two document vectors (−1 to 1)
- **percentage** = score clamped to 0–1 × 100

This is reported **separately** from the skill match and never combined into a single number.
Note that related documents typically score about 40–75%, so 70% semantic similarity is not
"70% qualified". It only means the texts are similar in topic and wording.

**Privacy:** everything runs locally. The CV is never stored or sent to an external service
(the only network access is the one-time model download from Hugging Face).

## Testing

```bash
pytest                                  # 98 tests, ~1 s, fully offline (1 opt-in test skipped)
RUN_EMBEDDING_TESTS=1 pytest            # also runs the opt-in test against the real embedding model (downloads it)
```

GitHub Actions (`.github/workflows/tests.yml`) runs the default suite on every push and pull request.

Coverage includes: health endpoint; CV upload validation (non-PDF, fake PDF, empty,
corrupted, oversized, too many pages, no text); job validation (missing, wrong type,
whitespace, too short/long, malformed JSON); skill extraction, aliases and token boundaries
(Java/JavaScript, C/C++/C#, Go vs. "good"/"going"/"go-to-market"); matching (high/low/partial/no
skills, every job skill is matched or missing, score formula); semantic service (with a fake
embedding model); and the full `/api/analyze` flow, including a check that internal errors return a generic 500.

## Limitations

- **Keyword-based skills:** negations ("no Java needed"), alternatives ("FastAPI *or* Flask" counts both as required), and skill level/years of experience are not understood.
- Only skills in the dictionary are detected; required vs. nice-to-have skills are weighted equally.
- Short case-sensitive skills can still occasionally match unrelated uses (e.g. "grade C", "Go" at the start of a sentence), and lowercase aliases like `ml` or `ts` can match non-skill uses ("5 ml").
- Scanned/image-only PDFs are rejected (no OCR). Multi-column PDF layouts may extract in an odd order.
- Semantic similarity reflects wording and topic, not qualification.
- English only.

## Future improvements

- Separate "required" and "nice to have" sections and weight them differently
- OCR fallback for scanned CVs
- Highlight where each matched skill appears in the CV
- Export the analysis as a PDF/Markdown report

## License

[MIT](LICENSE)
