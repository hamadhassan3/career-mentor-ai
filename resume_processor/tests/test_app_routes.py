import io


# -------------------------------------------------
# Simple GET endpoints
# -------------------------------------------------

def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "healthy"
    assert body["service"] == "resume-processor-api"
    assert "timestamp" in body


def test_get_skills(client):
    resp = client.get("/skills/all")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_get_designations(client):
    resp = client.get("/designations")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_get_it_categories(client):
    resp = client.get("/skills/it")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_get_languages(client):
    resp = client.get("/skills/languages")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_get_soft_skills(client):
    resp = client.get("/skills/soft")
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


# -------------------------------------------------
# /resumes/upload
# -------------------------------------------------

def test_upload_no_file_part(client):
    resp = client.post("/resumes/upload", data={})
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "No file part"


def test_upload_empty_filename(client):
    data = {"file": (io.BytesIO(b"data"), "")}
    resp = client.post("/resumes/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "No selected file"


def test_upload_success(client, app_mod, monkeypatch):
    parsed = {
        "total_exp": 4,
        "university": ["MIT"],
        "designition": ["Software Engineer"],
        "degree": ["BSc"],
        "skills": ["Python", "Teamwork", "English"],
        "Companies worked at": ["Acme"],
    }
    monkeypatch.setattr(app_mod, "safe_parse_resume_from_file", lambda path: parsed)
    monkeypatch.setattr(
        app_mod, "clean_skills",
        lambda skills: (["Python"], ["Backend"], ["Teamwork"], ["Soft"], ["English"], ["language"]),
    )
    monkeypatch.setattr(
        app_mod, "clean_designations",
        lambda raw: (["Software Engineer"], [""], ["Software Engineer"]),
    )

    data = {"file": (io.BytesIO(b"%PDF-1.4 fake"), "resume.pdf")}
    resp = client.post("/resumes/upload", data=data, content_type="multipart/form-data")

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total_exp"] == 4
    assert body["it_skills"] == ["Python"]
    assert body["soft_skills"] == ["Teamwork"]
    assert body["languages"] == ["English"]
    assert body["designition"] == ["Software Engineer"]
    assert body["companies_worked_at"] == ["Acme"]
    assert body["skills_original"] == ["Python", "Teamwork", "English"]
    assert "created_at" in body


def test_upload_parse_returns_none(client, app_mod, monkeypatch):
    monkeypatch.setattr(app_mod, "safe_parse_resume_from_file", lambda path: None)
    data = {"file": (io.BytesIO(b"data"), "resume.pdf")}
    resp = client.post("/resumes/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 500
    assert resp.get_json()["error"] == "Failed to parse resume"


def test_upload_parser_raises(client, app_mod, monkeypatch):
    def boom(path):
        raise RuntimeError("kaboom")

    monkeypatch.setattr(app_mod, "safe_parse_resume_from_file", boom)
    data = {"file": (io.BytesIO(b"data"), "resume.pdf")}
    resp = client.post("/resumes/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 500
    assert "kaboom" in resp.get_json()["error"]
