# Recommendation Service

A lightweight Flask microservice that powers the course-recommendation feature of **Career Mentor AI**. Given a search query (typically a skill or career topic), it aggregates relevant learning content from multiple online platforms and returns a normalized, unified list of courses.

It currently supports two sources:

- **Coursera** — discovered via HTML scraping of the public search page.
- **YouTube** — discovered via the official YouTube Data API v3 (playlist search).

The service is built around a pluggable **scraper factory**, so additional platforms can be registered without touching the HTTP layer.

---

## Table of Contents

- [Architecture](#architecture)
- [Major Libraries](#major-libraries)
- [Third-Party Services](#third-party-services)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Getting Started](#getting-started)
- [Running the Service](#running-the-service)
- [Testing & Code Coverage](#testing--code-coverage)
- [Extending: Adding a New Platform](#extending-adding-a-new-platform)
- [Project Structure](#project-structure)

---

## Architecture

```
HTTP request
     │
     ▼
┌─────────────┐      ┌──────────────────┐      ┌───────────────────────┐
│   app.py    │─────▶│  ScraperFactory  │─────▶│  <Platform>Scraper    │
│ (Flask app) │      │  (registry)      │      │  (BaseScraper subclass)│
└─────────────┘      └──────────────────┘      └───────────────────────┘
                                                          │
                                          ┌───────────────┴───────────────┐
                                          ▼                               ▼
                                  Coursera search page            YouTube Data API v3
                                  (HTML via requests +            (JSON via requests)
                                   BeautifulSoup)
```

- **`app.py`** — defines the Flask routes, validates input, invokes the right scraper(s), tags each result with its source platform, and returns JSON.
- **`scrapers/base_scraper.py`** — an abstract base class (`BaseScraper`) that provides a shared HTTP session, polite request throttling, safe HTML extraction helpers, and a `_standardize_course_data()` method that guarantees every platform returns the **same course schema**.
- **`scrapers/scraper_factory.py`** — a registry that maps a platform name (e.g. `"coursera"`) to its scraper class. New scrapers register here.
- **`scrapers/coursera_scraper.py`** / **`scrapers/youtube_scraper.py`** — concrete implementations.
- **`config.py`** — centralizes environment-driven settings (limits, per-platform toggles, CORS, logging).

Every scraper returns courses in this normalized shape:

```json
{
  "title": "Machine Learning",
  "link": "https://www.coursera.org/learn/machine-learning",
  "thumbnail": "https://...",
  "instructor": "Stanford University",
  "price": "",
  "rating": "",
  "platform": "coursera"
}
```

---

## Major Libraries

| Library | Version | Why it's used |
|---|---|---|
| **Flask** | 3.1.3 | Web framework that exposes the HTTP/JSON API. |
| **Flask-CORS** | 6.0.2 | Enables Cross-Origin Resource Sharing so the browser frontend can call this service directly. |
| **requests** | 2.33.1 | HTTP client used both for scraping the Coursera page and for calling the YouTube Data API. A shared `requests.Session` is reused per scraper. |
| **BeautifulSoup4** | 4.14.3 | HTML parsing for the Coursera scraper (`html.parser` backend); resilient selectors locate course cards. |
| **python-dotenv** | 1.x | Loads configuration from a local `.env` file during development. The import is optional — the app runs fine without it (e.g. when env vars are injected by the host). |
| **Werkzeug / Jinja2 / itsdangerous / click / blinker / MarkupSafe** | — | Transitive dependencies of Flask. |
| **pytest / pytest-cov** | dev only | Test runner and coverage measurement (see [Testing & Code Coverage](#testing--code-coverage)). |

> The full pinned dependency set lives in `requirements.txt`. A `Pipfile` is also provided for `pipenv` users, with `pytest`/`pytest-cov` declared under `[dev-packages]`.

---

## Third-Party Services

### 1. YouTube Data API v3 *(requires an API key)*

- **Endpoint used:** `GET https://www.googleapis.com/youtube/v3/search`
- **Query strategy:** searches for `type=playlist` matching `"<query> course tutorial playlist"`, ordered by relevance.
- **What we extract:** title, playlist URL, best-available thumbnail, and channel name (treated as the "instructor"). Price is set to `"Free"`.
- **Authentication:** an API key supplied via the `YOUTUBE_API_KEY` environment variable. **The YouTube scraper raises a `ValueError` on instantiation if this key is missing.**
- **Get a key:** [Google Cloud Console](https://console.cloud.google.com/) → enable *YouTube Data API v3* → create an API key. Be mindful of the daily quota (default 10,000 units/day; a search call costs ~100 units).

### 2. Coursera *(public web scraping — no key)*

- **Source:** the public Coursera search page at `https://www.coursera.org/search`.
- **Method:** an HTML page request via `requests`, parsed with BeautifulSoup. The scraper tries several CSS/`data-testid` selectors to find course cards and falls back to scanning `/learn/` and `/specializations/` anchor links if the layout changes.
- **No authentication required.**
- ⚠️ **Caveat:** because this relies on Coursera's page structure (not an official API), it can break if Coursera changes their markup. The scraper is written defensively (multiple selector fallbacks, exception-safe parsing) and degrades gracefully by returning an empty list rather than erroring out. Requests are lightly throttled (`time.sleep` with a randomized delay) to remain polite.

> **Note on unused settings:** the sample `.env` includes keys for additional integrations that are scaffolded but **not implemented** in the current code: `GITHUB_TOKEN`, `EDX_API_KEY`, `EDX_ENABLED`, and `FREECODECAMP_ENABLED`. They are safe to omit.

---

## API Reference

Base URL (development): `http://localhost:5051`

All search endpoints accept a JSON body and return JSON.

### `GET /health`
Health probe. Returns service status and the list of registered platforms.
```json
{
  "status": "healthy",
  "message": "Course recommendation service is running",
  "available_platforms": ["coursera", "youtube"]
}
```

### `GET /platforms`
Returns the platforms currently registered with the scraper factory.
```json
{ "platforms": ["coursera", "youtube"] }
```

### `POST /courses/coursera`
Search Coursera only.

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `query` | string | ✅ | — | Search term. |
| `limit` | int | ❌ | `10` | Max results to return. |

```bash
curl -X POST http://localhost:5051/courses/coursera \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "limit": 5}'
```
Returns `400` if `query` is empty, `500` on an internal error.

### `POST /courses/youtube`
Search YouTube only. Same request fields as above.
```bash
curl -X POST http://localhost:5051/courses/youtube \
  -H "Content-Type: application/json" \
  -d '{"query": "python", "limit": 5}'
```

### `POST /courses/search`
Aggregate search across multiple platforms.

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `query` | string | ✅ | — | Search term. |
| `platforms` | string[] | ❌ | `["coursera", "youtube"]` | Which sources to query. |
| `limit` | int | ❌ | `10` | Fallback per-platform cap for platforms without a specific cap. |

> Per-platform result caps (currently `coursera: 2`, `youtube: 2`) are applied to keep the combined response concise. If one platform fails, the others still return; the failing platform reports `count: 0` with an `error` message instead of failing the whole request.

```bash
curl -X POST http://localhost:5051/courses/search \
  -H "Content-Type: application/json" \
  -d '{"query": "data science", "platforms": ["coursera", "youtube"]}'
```

Response shape:
```json
{
  "query": "data science",
  "total_results": 4,
  "platforms_searched": ["coursera", "youtube"],
  "platform_breakdown": {
    "coursera": { "count": 2, "courses": [ ... ] },
    "youtube":  { "count": 2, "courses": [ ... ] }
  },
  "courses": [ ... ]
}
```

---

## Configuration

Configuration is driven by environment variables (loaded from `.env` in development via `python-dotenv`). Defaults are defined in `config.py`.

| Variable | Default | Description |
|---|---|---|
| `DEBUG` | `True` | Flask debug mode. |
| `HOST` | `0.0.0.0` | Bind host. |
| `PORT` | `5000` (config) / **`5051`** (app entrypoint) | See note below. |
| `DEFAULT_COURSE_LIMIT` | `10` | Default result limit. |
| `MAX_COURSE_LIMIT` | `50` | Upper bound for limits. |
| `REQUEST_DELAY` | `1.0` | Base delay between scraper requests (seconds). |
| `REQUEST_TIMEOUT` | `10` | HTTP request timeout (seconds). |
| `RETRY_ATTEMPTS` | `3` | Configured retry attempts. |
| `COURSERA_ENABLED` | `True` | Toggle the Coursera platform config. |
| `YOUTUBE_ENABLED` | `True` | Toggle the YouTube platform config. |
| `YOUTUBE_API_KEY` | — | **Required** for YouTube search. |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins. |
| `LOG_LEVEL` | `INFO` | Logging level. |

> **Port note:** `config.py` defaults `PORT` to `5000`, but the development entrypoint in `app.py` (`app.run(...)`) hardcodes port **`5051`**, which matches the sample `.env`. When running via `python app.py`, the service listens on **5051**.

A starter `.env` is included in the repo — copy it and fill in your own `YOUTUBE_API_KEY`.

---

## Getting Started

### Prerequisites
- Python **3.13** (per `Pipfile`)
- A **YouTube Data API v3** key (only needed if you want YouTube results)

### Option A — pip + venv

```bash
cd recommendation_service
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Option B — pipenv

```bash
cd recommendation_service
pipenv install --dev               # includes pytest / pytest-cov
pipenv shell
```

### Set up environment variables

Create a `.env` file in `recommendation_service/`:

```dotenv
YOUTUBE_API_KEY=your_youtube_api_key_here
PORT=5051
CORS_ORIGINS=*
LOG_LEVEL=INFO
```

---

## Running the Service

```bash
python app.py
```

The service starts on `http://0.0.0.0:5051`. Verify it's up:

```bash
curl http://localhost:5051/health
```

For production, run behind a WSGI server (e.g. `gunicorn`/`waitress`) and a reverse proxy rather than the Flask dev server.

---

## Testing & Code Coverage

The service ships with a comprehensive **unit test suite at 100% code coverage**. All external I/O (HTTP requests, the YouTube API, and Coursera HTML) is **mocked**, so the tests are fast, deterministic, and require **no network access or API key**.

### Run the tests

```bash
# pip/venv
pytest

# pipenv
pipenv run pytest
```

Coverage is configured in `setup.cfg` and runs automatically with every `pytest` invocation. The build is **gated at 100%** (`--cov-fail-under=100`) — the suite fails if coverage drops below that threshold.

### Current coverage

```
Name                           Stmts   Miss  Cover
------------------------------------------------------------
app.py                            80      0   100%
config.py                         15      0   100%
scrapers/__init__.py               0      0   100%
scrapers/base_scraper.py          43      0   100%
scrapers/coursera_scraper.py      63      0   100%
scrapers/scraper_factory.py       21      0   100%
scrapers/youtube_scraper.py       51      0   100%
------------------------------------------------------------
TOTAL                            273      0   100%
59 passed
```

### What's covered
- All HTTP routes, including success, missing-query (`400`), and error (`500`) paths.
- Both scrapers' parsing logic, selector fallbacks, and graceful-failure behavior.
- The scraper factory (lookup, registration, unsupported-platform errors).
- `BaseScraper` request handling and URL/data normalization branches.
- The optional `python-dotenv` import fallback.

The only line excluded from coverage is the `if __name__ == '__main__':` dev-server launcher (standard practice), configured via `exclude_lines` in `setup.cfg`.

### Test layout
```
conftest.py                 # shared fixtures (Flask test client, env setup)
setup.cfg                   # pytest + coverage configuration
tests/
├── test_app.py             # Flask routes
├── test_config.py          # configuration helpers
├── test_base_scraper.py    # BaseScraper behavior
├── test_scraper_factory.py # factory registry
├── test_coursera_scraper.py
└── test_youtube_scraper.py
```

---

## Extending: Adding a New Platform

1. Create a new scraper in `scrapers/` that subclasses `BaseScraper` and implements `search_courses()` and `_parse_course_card()`. Return results via `self._standardize_course_data(...)` so the output schema stays consistent.
2. Register it with the factory in `scrapers/scraper_factory.py`:
   ```python
   ScraperFactory.register_scraper("udemy", UdemyScraper)
   ```
3. (Optional) Add a dedicated route in `app.py`, or rely on the generic `/courses/search` endpoint by passing your platform name in the `platforms` array.
4. Add tests and keep coverage at 100%.

---

## Project Structure

```
recommendation_service/
├── app.py                       # Flask application & routes
├── config.py                    # environment-driven configuration
├── requirements.txt             # pinned runtime dependencies (pip)
├── Pipfile                      # pipenv dependencies (+ dev tools)
├── setup.cfg                    # pytest & coverage config
├── conftest.py                  # test fixtures
├── .env                         # local environment variables (not committed)
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py          # abstract base + shared helpers
│   ├── scraper_factory.py       # platform registry
│   ├── coursera_scraper.py      # Coursera (HTML scraping)
│   └── youtube_scraper.py       # YouTube (Data API v3)
└── tests/                       # unit tests (100% coverage)
```
