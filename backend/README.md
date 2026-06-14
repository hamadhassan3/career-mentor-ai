# Career Mentor AI — Backend (Django)

The Django backend is the central service of the **Career Mentor AI** (FawkesPath)
platform. It sits between the React frontend and the supporting Python
microservices, owning authentication, persistence, and orchestration of all
AI-powered features (career chat, daily nudges, resume insights, and progress
tracking).

```
                ┌──────────────┐
   React  ─────▶│   Django     │─────▶ Resume Processor service (skills/parsing)
  frontend      │   backend    │─────▶ Recommendation service (courses/videos)
                │  (this repo) │─────▶ Gemini LLM (direct, or via AWS Lambda proxy)
                └──────┬───────┘─────▶ Langfuse (LLM observability)
                       │       └─────▶ AWS S3 (progress images)
                       ▼
                  PostgreSQL
```

---

## Table of contents

- [Architecture](#architecture)
- [Apps & responsibilities](#apps--responsibilities)
- [Major libraries](#major-libraries)
- [Third-party services](#third-party-services)
- [API overview](#api-overview)
- [Getting started](#getting-started)
- [Environment variables](#environment-variables)
- [Running the server](#running-the-server)
- [Testing & code coverage](#testing--code-coverage)
- [Project layout](#project-layout)

---

## Architecture

- **Framework:** Django 6.0 + Django REST Framework.
- **Auth:** JWT access/refresh tokens (`djangorestframework-simplejwt`) with
  optional **TOTP two-factor authentication** (`pyotp`).
- **Database:** PostgreSQL in all real environments; tests run on in-memory
  SQLite.
- **AI orchestration:** The `chat` and `nudge` apps build user-specific context
  from the database, call an LLM through LangChain, and log every call to
  Langfuse.
- **Microservice integration:** The `resume_processor` app is a transparent
  reverse proxy to the resume-parsing service; the `resumes` app calls the
  course-recommendation service and caches results.

---

## Apps & responsibilities

| App | Responsibility |
| --- | --- |
| `users` | Registration, JWT login, TOTP 2FA setup/verification, password change & reset-by-email. |
| `resumes` | Resume CRUD, the single "active resume" rule, Next Best Step & Career Pathway recommendations, cached course recommendations. |
| `chat` | Career-mentor conversational AI — conversation/message persistence, prompt building, LLM calls, Langfuse tracing. |
| `nudge` | Daily motivational "nudge" generation (LLM-backed) with 24-hour freshness and graceful fallbacks. |
| `progress` | Skill-achievement images uploaded to and served from AWS S3 via presigned URLs. |
| `resume_processor` | HTTP reverse proxy forwarding skill/parsing requests to the external resume-processor microservice. |

> `analytics`, `career_paths`, and `skills` are scaffolded apps reserved for
> future work and currently contain no business logic.

---

## Major libraries

| Library | Version | Used for |
| --- | --- | --- |
| **Django** | 6.0.4 | Web framework, ORM, migrations, admin. |
| **djangorestframework** | 3.17 | REST API views, serializers, permissions. |
| **djangorestframework-simplejwt** | 5.5 | JWT access/refresh token authentication. |
| **PyJWT** | 2.12 | JWT primitives underlying SimpleJWT. |
| **pyotp** | 2.9 | TOTP secret generation & verification (2FA). |
| **psycopg2-binary** | 2.9 | PostgreSQL driver. |
| **django-cors-headers** | 4.9 | CORS handling for the React frontend. |
| **boto3 / botocore** | 1.43 | AWS S3 uploads, deletes, and presigned URLs. |
| **requests** | 2.33 | Outbound calls to the recommendation & resume-processor services and the LLM proxy. |
| **LangChain** (`langchain`, `langchain-core`, `langchain-google-genai`) | 1.x | LLM message abstractions and the Gemini chat model. |
| **langfuse** | 4.6 | LLM observability / tracing of prompts and responses. |
| **python-dotenv** | 1.2 | Loading configuration from `.env`. |
| **Pillow** | 12.x | Image validation for uploaded progress images. |
| **pytest / pytest-django / pytest-cov / coverage** | latest | Test runner and coverage measurement (dev only). |

---

## Third-party services

| Service | Purpose | Configured via | Degraded behavior |
| --- | --- | --- | --- |
| **Google Gemini** (`gemini-3.1-flash-lite`) | Generates chat replies and nudges. In development the model is called directly; in production it is reached through an **AWS Lambda proxy**. | `GOOGLE_API_KEY`, `LLM_PROXY_URL`, `ENVIRONMENT` | Returns a friendly "service unavailable" message; never 500s the request. |
| **AWS Lambda LLM proxy** | Public, Gemini-backed proxy used in production so no API key ships to the client. | `LLM_PROXY_URL` | Falls back to the unavailable message. |
| **Langfuse** | Traces every LLM call (prompt, response, model, tokens) for debugging and analytics. Calls are fire-and-forget on a background thread pool. | `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_HOST` | Silently disabled if no secret key is set. |
| **AWS S3** | Stores progress-achievement images; serves them via short-lived presigned URLs. | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_REGION`, `AWS_S3_BUCKET_NAME` | Upload endpoints return a clear error response. |
| **Recommendation service** | Returns Coursera courses and YouTube videos for a user's next skill; results are cached on `SkillCourseRecommendation`. | `COURSE_RECOMMENDATION_API_BASE_URL` | Returns `503` with an empty course list. |
| **Resume-processor service** | Parses resumes and predicts skills/designations; proxied transparently. | `RESUME_PROCESSOR_API_BASE_URL` | Returns `503` (unreachable) or `500` (not configured). |
| **SMTP email** | Sends password-reset links. | `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` | Reset requests always return success to prevent email enumeration. |

---

## API overview

All endpoints are mounted under `/api/` (see `career_mentor_ai/urls.py`).

### Auth — `/api/auth/`
| Method | Path | Description |
| --- | --- | --- |
| POST | `register/` | Create a new account. |
| POST | `login/` | Username/password login; returns tokens or a TOTP challenge. |
| POST | `token/refresh/` | Refresh a JWT access token. |
| GET/PATCH | `me/` | Read/update the current user. |
| GET | `totp/setup/` | Generate a TOTP secret & provisioning URI. |
| POST | `totp/confirm/` | Confirm TOTP setup with a code. |
| POST | `totp/login/` | Complete login with a TOTP code. |
| POST | `change-password/` | Change password (authenticated). |
| POST | `password-reset/` | Request a reset email. |
| POST | `password-reset/confirm/` | Set a new password from the emailed token. |

### Resumes — `/api/resumes/`
List/create, detail (`<pk>/`), `<pk>/activate/`, `upload/`, `latest/`,
`active/`, `next-step/` (+ `save/`), `career-pathway/` (+ `save/`),
`recommendations/clear/`, and `courses/`.

### Chat — `/api/chat/`
`GET` conversation history (latest or by `conversation_id`); `POST` a message
to receive an AI reply.

### Nudge — `/api/nudge/`
`GET` the daily nudge (generated if stale); `POST` to force regeneration.

### Progress — `/api/progress/`
`achievements/` (list), `achievements/create/`, `achievements/<id>/delete/`.

### Resume processor proxy — `/api/resume-processor/`
`resumes/upload`, `skills/all|it|soft|languages`, `designations`, `predict`,
`predict_next_skill`.

---

## Getting started

### Prerequisites
- Python **3.13**
- PostgreSQL
- [pipenv](https://pipenv.pypa.io/) (a `Pipfile` is provided; `requirements.txt`
  is also available for plain `pip`)

### Install

```bash
# With pipenv (recommended)
pipenv install
pipenv shell

# …or with pip + a virtualenv
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Configure
Create a `.env` file in this directory (see
[Environment variables](#environment-variables)).

### Migrate

```bash
python manage.py migrate
python manage.py createsuperuser   # optional, for the Django admin
```

---

## Environment variables

Configuration is loaded from `.env` via `python-dotenv`. **Never commit real
secrets.** The keys below are read by `career_mentor_ai/settings.py` and the
service modules:

```ini
# Core
SECRET_KEY=
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
ENVIRONMENT=development          # 'production' switches the LLM to the Lambda proxy
APP_NAME=Career Mentor

# Database (PostgreSQL)
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

# CORS / frontend
CORS_ALLOWED_ORIGINS=http://localhost:3000
FRONTEND_URL=http://localhost:3000

# Email (SMTP) — password reset
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=

# Microservices
COURSE_RECOMMENDATION_API_BASE_URL=http://localhost:5051
RESUME_PROCESSOR_API_BASE_URL=

# LLM (Gemini)
GOOGLE_API_KEY=                  # used in development (direct Gemini)
LLM_PROXY_URL=                   # used in production (AWS Lambda proxy)

# Langfuse (LLM observability)
LANGFUSE_SECRET_KEY=
LANGFUSE_PUBLIC_KEY=
LANGFUSE_HOST=https://cloud.langfuse.com

# AWS S3 (progress images)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_REGION=us-east-1
AWS_S3_BUCKET_NAME=
```

Most AI/storage integrations **degrade gracefully** when their keys are absent,
so the server boots and core flows work even with a minimal `.env`.

---

## Running the server

```bash
python manage.py runserver        # http://127.0.0.1:8000
```

In production the service runs behind nginx on the platform VM (WSGI via
`career_mentor_ai/wsgi.py`).

---

## Testing & code coverage

The suite uses **pytest** + **pytest-django** and runs against an in-memory
SQLite database (`career_mentor_ai/test_settings.py`), so no PostgreSQL, S3,
SMTP, or live LLM/microservice access is required — all external calls are
mocked.

```bash
# Run the full suite with a coverage report
pytest

# Run a single app's tests without coverage
pytest users/tests.py --no-cov
```

Configuration lives in `pytest.ini` and `.coveragerc`. Coverage is measured over
the six apps that contain business logic: `users`, `resumes`, `chat`, `nudge`,
`progress`, and `resume_processor`.

### Current coverage

**Overall: ~98% line coverage across 165 tests.**

| Module | Coverage |
| --- | --- |
| `users` (models, serializers, views) | 100% |
| `chat` (models, services, views) | 96–100% |
| `nudge` (model, service, views) | 96–100% |
| `progress` (model, serializers, services, views) | 97–100% |
| `resumes` (models, serializers, views, constants) | 92–100% |
| `resume_processor` (proxy views) | 100% |

The small remaining gaps are defensive `except Exception → HTTP 500` branches.
The suite comfortably exceeds the project's 80% coverage target.

---

## Project layout

```
backend/
├── career_mentor_ai/      # Project config (settings, urls, wsgi/asgi, test_settings)
├── users/                 # Auth + TOTP 2FA
├── resumes/               # Resumes, Next Best Step, Career Pathway, course cache
├── chat/                  # Conversational AI (services/: chat, llm, prompt, langfuse)
├── nudge/                 # Daily nudges (services/: nudge)
├── progress/              # S3-backed achievement images
├── resume_processor/      # Reverse proxy to the resume-processor microservice
├── analytics/ career_paths/ skills/   # Reserved (no logic yet)
├── manage.py
├── pytest.ini             # pytest-django + coverage config
├── .coveragerc            # coverage settings
├── requirements.txt       # pip dependencies
└── Pipfile                # pipenv dependencies
```
