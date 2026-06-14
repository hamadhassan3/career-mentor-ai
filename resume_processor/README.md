# Resume Processor

A Flask microservice that powers the resume-understanding and skill-recommendation features of **Career Mentor AI**.

It does two distinct jobs:

1. **Resume parsing & normalization** — accepts an uploaded resume (PDF / DOCX / TXT), extracts raw fields (skills, designations, education, experience, companies), and maps the messy free-text skills onto a **standardized vocabulary**, split into IT skills, soft skills, and spoken languages.
2. **"Next skill" recommendation** — given a user's current skills and a target designation, predicts which skills they should learn next using two trained models: a multi-output **LSTM** (`/predict`) and a single-best-skill **XGBoost** classifier (`/predict_next_skill`).

The standardized skill/designation vocabularies and the trained models are all loaded **once at startup** and held in memory, so request handling stays fast and fully self-contained (no external API calls at request time).

---

## Table of Contents

- [Architecture](#architecture)
- [Major Libraries](#major-libraries)
- [Third-Party Services & Assets](#third-party-services--assets)
- [The resume-parser Patch](#the-resume-parser-patch)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Getting Started](#getting-started)
- [Running the Service](#running-the-service)
- [Testing & Code Coverage](#testing--code-coverage)
- [Project Structure](#project-structure)

---

## Architecture

```
                                  ┌──────────────────────────────────────────┐
                                  │                app.py                     │
                                  │  (Flask app — routes, request validation) │
                                  └───────────────┬──────────────────────────┘
                                                  │
        ┌─────────────────────────────────────────┼─────────────────────────────────────────┐
        ▼                                          ▼                                          ▼
┌──────────────────┐                 ┌──────────────────────────┐                ┌──────────────────────────┐
│  /resumes/upload │                 │        /predict          │                │   /predict_next_skill    │
│                  │                 │     (LSTM, multi-out)    │                │     (XGBoost, top-1)     │
└────────┬─────────┘                 └────────────┬─────────────┘                └────────────┬─────────────┘
         │                                        │                                           │
         ▼                                        ▼                                           ▼
┌────────────────────────┐          ┌──────────────────────────┐              ┌──────────────────────────────┐
│ scripts/extract_resume │          │  model/lstm_model.keras  │              │ model/single_skill_xgboost.pkl│
│  → resume_parser (Tika │          │  + *_tokenizer.json      │              │  (XGBoost + sklearn          │
│    / pdfminer / spaCy) │          │  + config.json           │              │   LabelEncoder, pickled)     │
└───────────┬────────────┘          └──────────────────────────┘              └──────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────────┐
│  scripts/clean_skills_new.py                  │   standardize raw skills →
│  scripts/clean_designations_new.py            │   IT / soft / language buckets
│  scripts/extract_occupations_new.py           │   + cleaned designations
│      (pandas over scripts/data/*.csv|json)    │
└──────────────────────────────────────────────┘
```

- **`app.py`** — defines the Flask routes, performs request validation, runs the parsing/cleaning pipeline or model inference, and returns JSON. At import time it loads the trained model, the three tokenizers, the runtime config, and the standardized vocabularies.
- **`scripts/extract_resume.py`** — thin, defensive wrapper around the third-party `resume_parser` library. Saves the upload to a temp file, parses it, and scrubs Unicode/surrogate noise from the result.
- **`scripts/clean_skills_new.py`** — loads the IT-skill, soft-skill, and language vocabularies from CSV and fuzzy-matches each raw resume skill to a standardized entry (using `difflib.SequenceMatcher`), separating results into **IT / soft / language** buckets.
- **`scripts/clean_designations_new.py`** — loads job-title and ML-trained-designation vocabularies and fuzzy-matches raw resume job titles to standardized designations.
- **`scripts/extract_occupations_new.py`** — derives the IT occupation/category list from the job-roles dataset.
- **`model/`** — the trained artifacts (see [Third-Party Services & Assets](#third-party-services--assets)).
- **`scripts/data/`** — the reference datasets (CSV/JSON) the vocabularies are built from.

---

## Major Libraries

| Library | Version | Why it's used |
|---|---|---|
| **Flask** | 3.1.3 | Web framework that exposes the HTTP/JSON API. Served with the built-in WSGI server in `threaded` mode. |
| **TensorFlow / Keras** | 2.21.0 / 3.x | Loads and runs `lstm_model.keras` for the `/predict` multi-output next-skill model. Memory growth is configured at startup and oneDNN/verbose logging are disabled to keep the footprint small. |
| **XGBoost** | 3.2.0 | Gradient-boosted classifier behind `/predict_next_skill`; predicts the single best next skill from a wide one-hot feature vector. |
| **scikit-learn** | (transitive) | Provides the `LabelEncoder` that is pickled alongside the XGBoost model and used to map class indices back to skill labels. |
| **pandas** | 3.0.2 | Reads all reference datasets (`scripts/data/*.csv`) and builds the feature DataFrame for XGBoost inference. |
| **NumPy** | 2.4.4 | Array math for thresholding, sorting prediction scores, and assembling model inputs. |
| **resume-parser** | 0.8.4 | Third-party resume parser that extracts structured fields from PDF/DOCX/TXT. **Requires a local patch — see below.** |
| **spaCy** + **en_core_web_sm** | 3.8.14 | NLP backbone used by `resume_parser` for entity/section extraction. The English model is pinned in the dependencies. |
| **NLTK** | 3.9.4 | Tokenization/stopword support used by `resume_parser`. May require one-time corpus downloads. |
| **pdfplumber / pdfminer.six / pypdfium2** | — | PDF text extraction backends used during resume parsing. |
| **docx2txt** | 0.9 | DOCX text extraction. |
| **tika** | 3.1.0 | Apache Tika Python binding — the **default** parsing backend used by `resume_parser` for PDF/DOCX. Tika runs on the JVM, so a Java runtime is required (see [Third-Party Services & Assets](#third-party-services--assets)). |
| **phonenumbers** | 9.0.29 | Phone-number detection within resumes. |
| **pytest / pytest-cov** | dev only | Test runner and coverage measurement (see [Testing & Code Coverage](#testing--code-coverage)). |

> Dependency management uses **pipenv** (`Pipfile`, Python 3.13). A flat `requirements.txt` is also provided for `pip`-based installs.

---

## Third-Party Services & Assets

This service makes **no outbound network calls at request time** — all intelligence ships with the service. The "third-party" pieces are runtime dependencies and bundled assets rather than remote APIs:

### Apache Tika (JVM)

`resume_parser` uses **Apache Tika as its default extraction backend** (`read_file(..., docx_parser="tika")` → `tika.parser.from_file(...)` for both PDF and DOCX). Tika runs on the JVM, so a **Java runtime (JRE/JDK) must be available on the host**, and on first use the Tika server JAR is downloaded and started locally. In the broader Career Mentor AI deployment this service runs on a single VM alongside the other backends.

### Trained model artifacts — `model/`

| File | Purpose |
|---|---|
| `lstm_model.keras` | Multi-output LSTM that predicts next **IT** and **soft** skills from current skills + target designation. Used by `/predict`. |
| `single_skill_xgboost.pkl` | Pickled dict bundling the XGBoost model, a sklearn `LabelEncoder`, the training `feature_columns`, and the skill/profession vocabularies. Used by `/predict_next_skill`. |
| `it_tokenizer.json` | Keras tokenizer mapping IT-skill tokens → indices. |
| `soft_tokenizer.json` | Keras tokenizer for soft-skill tokens. |
| `designation_tokenizer.json` | Keras tokenizer for target designations. |
| `config.json` | Runtime config: `MAX_IT_LEN`, `MAX_SOFT_LEN`, embedding dims, and `model_version`. |

### Reference datasets — `scripts/data/`

| File | Used by | Purpose |
|---|---|---|
| `it_job_roles_skills.csv` | skills, designations, occupations | Master IT job-role → skills mapping; source of the IT-skill and job-title vocabularies. |
| `soft_skills.csv` | `clean_skills_new` | Soft-skill vocabulary. |
| `languages.csv` | `clean_skills_new` | Spoken-language vocabulary (with ISO codes). |
| `processed/designation_aggregated_skills.json` | `clean_designations_new` | The exact designations the recommendation models were trained on. |
| `acs_it_occupations.csv`, `anzsco_occupations.csv` | (legacy) | Older occupation sources; the current code keeps the function signature for compatibility but no longer reads them. |

> The `scripts/data/processed/` folder also contains large intermediate training corpora (`parsed_resumes.json`, `training_data.json`, etc.). These are **only used for (re)training in the notebooks** and are **not** needed at runtime.

---

## The resume-parser Patch

The pinned `resume-parser==0.8.4` release needs a small patch to run correctly under this environment. A patch and cross-platform applier are included:

| File | Purpose |
|---|---|
| `resume-parser-patch.txt` | The patched contents of the parser module. |
| `apply_resume_parser_patch.py` | Locates the installed `resume_parser` package, backs up the original module, and applies the patch (then verifies the import). |
| `apply_patch.sh` / `apply_patch.bat` | Convenience wrappers for Unix/macOS and Windows. |

Apply it **after** installing dependencies and **before** starting the service:

```bash
# macOS / Linux
./apply_patch.sh
# or directly
python3 apply_resume_parser_patch.py
```

```bat
:: Windows
apply_patch.bat
```

The applier creates a `.py.backup` of the original module, so it is safe to re-run.

---

## API Reference

All responses are JSON. The service listens on **port `5050`** by default.

### `GET /health`

Liveness probe.

```json
{ "status": "healthy", "timestamp": "2026-06-14T12:00:00.000000", "service": "resume-processor-api" }
```

### Vocabulary endpoints

Each returns a sorted JSON array of standardized names loaded at startup.

| Endpoint | Returns |
|---|---|
| `GET /skills/all` | All standardized IT skills. |
| `GET /designations` | All standardized designations (ML-trained set). |
| `GET /skills/it` | IT skills. *(Currently returns the same list as `/skills/all`.)* |
| `GET /skills/languages` | Spoken languages. |
| `GET /skills/soft` | Soft skills. |

### `POST /resumes/upload`

Parses an uploaded resume and returns standardized fields.

- **Content-Type:** `multipart/form-data`
- **Field:** `file` — a PDF / DOCX / TXT resume.

```bash
curl -F "file=@resume.pdf" http://localhost:5050/resumes/upload
```

**Response (`200`):**

```json
{
  "total_exp": 4,
  "university": ["..."],
  "designition": ["Software Engineer"],
  "degree": ["BSc"],
  "skills": ["Python", "..."],
  "companies_worked_at": ["Acme"],
  "skills_original": ["python", "team work", "..."],
  "it_skills": ["Python", "..."],
  "it_skill_categories": ["Backend Developer", "..."],
  "soft_skills": ["Teamwork", "..."],
  "soft_skill_categories": ["Soft Skill", "..."],
  "languages": ["English", "..."],
  "language_categories": ["language", "..."],
  "created_at": "2026-06-14T12:00:00.000000"
}
```

> Note: `designition` (sic) mirrors the key emitted by the underlying parser library and is preserved intentionally.

**Errors:** `400` if no `file` part / empty filename; `500` if parsing fails.

### `POST /predict`  — LSTM next-skill model

- **Content-Type:** `application/json`

```json
{
  "it_skill_categories": ["Python", "Django"],
  "soft_skills": ["Communication"],
  "desired_designation": "Backend Engineer"
}
```

**Response (`200`):**

```json
{
  "predicted_next_it_skills": ["docker", "..."],
  "predicted_next_soft_skills": ["leadership", "..."],
  "note": "Predictions exclude skills you already have"
}
```

Skills already supplied in the request are excluded from the suggestions. A confidence-aware dynamic threshold controls how many predictions are returned (up to 10 IT + 8 soft). Errors return `500` with `{ "error": "..." }`.

### `POST /predict_next_skill`  — XGBoost single best skill

Same request body as `/predict`.

**Response (`200`):**

```json
{
  "best_next_skill": { "skill": "kubernetes", "type": "IT", "confidence": 0.83 },
  "top_3_skills": [ { "skill": "kubernetes", "type": "IT", "confidence": 0.83 }, "..." ]
}
```

`best_next_skill` is `null` when no new skill can be suggested. Errors return `500`; if the model file is missing the message is `"Single skill model not found. Please train the model first."`

---

## Configuration

| Variable | Default | Effect |
|---|---|---|
| `FLASK_DEBUG` | `False` | Set to `true` to enable Flask debug mode (kept off in production to reduce memory use). |
| `TF_CPP_MIN_LOG_LEVEL` | `2` (set in code) | Suppresses verbose TensorFlow logs. |
| `TF_ENABLE_ONEDNN_OPTS` | `0` (set in code) | Disables oneDNN optimizations to save memory. |

Model and data paths are resolved **relative to the service directory**, so the app should be started from `resume_processor/` (e.g. `./model/lstm_model.keras`).

---

## Getting Started

### Prerequisites

- **Python 3.13**
- **pipenv** (`pip install pipenv`)
- A **Java runtime** (JRE/JDK) — required, since `resume_parser` parses PDF/DOCX through Apache Tika by default.

### Install

```bash
cd resume_processor

# Option A — pipenv (recommended; matches Pipfile)
pipenv install
pipenv shell

# Option B — pip + virtualenv
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Post-install steps

```bash
# 1. Patch the resume-parser library (required)
python3 apply_resume_parser_patch.py

# 2. (If needed) download NLTK corpora used by the parser
python3 -m nltk.downloader punkt stopwords
```

The spaCy English model (`en_core_web_sm`) is pinned as a dependency and installs automatically; no separate download step is required.

---

## Running the Service

```bash
# from the resume_processor/ directory
python3 app.py
# → serves on http://0.0.0.0:5050
```

Quick smoke test:

```bash
curl http://localhost:5050/health
```

---

## Testing & Code Coverage

The suite uses **pytest** with **pytest-cov** and enforces **100% statement coverage** (`--cov-fail-under=100`, configured in `setup.cfg`).

```bash
# from the resume_processor/ directory
pipenv run pytest
# or, inside an activated venv:
pytest
```

Coverage is gated over `app.py` and the four runtime `scripts` modules (`clean_skills_new`, `clean_designations_new`, `extract_occupations_new`, `extract_resume`).

Notes on the test design (`conftest.py`, `tests/`):

- The **TensorFlow/Keras stack is stubbed** in `conftest.py` before `app.py` is imported, so tests run fast and deterministically without loading the real `.keras` model. Model predictions are wired with controlled fakes per test.
- The **data-loading helpers run for real** against the small CSV/JSON files in `scripts/data/`, so the vocabulary endpoints return realistic payloads.
- Tests must be run **from the service directory** because the app uses relative paths for model/config files.
- A couple of genuinely unreachable defensive branches in `clean_skills_new.py` are marked `# pragma: no cover` (documented inline).

---

## Project Structure

```
resume_processor/
├── app.py                          # Flask app: routes + startup model/vocab loading
├── conftest.py                     # pytest fixtures; stubs TensorFlow for fast tests
├── setup.cfg                       # pytest + coverage config (100% gate)
├── Pipfile / requirements.txt      # dependencies (pipenv / pip)
│
├── apply_resume_parser_patch.py    # patches the installed resume_parser package
├── apply_patch.sh / apply_patch.bat
├── resume-parser-patch.txt         # patched parser module contents
│
├── model/                          # trained artifacts (LSTM, XGBoost, tokenizers, config)
│
├── scripts/
│   ├── extract_resume.py           # resume_parser wrapper + Unicode scrubbing
│   ├── clean_skills_new.py         # IT / soft / language skill standardization
│   ├── clean_designations_new.py   # designation standardization
│   ├── extract_occupations_new.py  # IT occupation/category extraction
│   ├── *.ipynb                     # training / data-prep notebooks (not used at runtime)
│   └── data/                       # reference datasets (CSV/JSON) + training corpora
│
└── tests/                          # pytest suite (100% coverage of runtime modules)
```

> The `scripts/` folder also contains legacy modules (`clean_skills.py`, `clean_designations.py`, `extract_occupations.py`) that predate the `*_new` versions and are **not** imported by the running service.
