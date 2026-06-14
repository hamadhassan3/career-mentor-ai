import scripts.extract_resume as er


# -------------------------------------------------
# clean_unicode_text
# -------------------------------------------------

def test_clean_unicode_text_strips_surrogate_markers():
    assert er.clean_unicode_text("hi\\ud83dthere") == "hithere"


def test_clean_unicode_text_coerces_non_string():
    assert er.clean_unicode_text(123) == "123"


# -------------------------------------------------
# safe_parse_resume_from_file
# -------------------------------------------------

def test_safe_parse_from_file_cleans_values(monkeypatch):
    raw = {
        "skills": ["Python", None, 42],   # list with str, None, non-str
        "name": "Jo\\ud83dhn",            # str value cleaned
        "total_exp": 5,                    # non-str value kept
        "empty": None,                     # None value dropped
    }
    monkeypatch.setattr(er.resumeparse, "read_file", lambda path: raw)

    result = er.safe_parse_resume_from_file("whatever.pdf")
    assert result["skills"] == ["Python", 42]
    assert result["name"] == "John"
    assert result["total_exp"] == 5
    assert "empty" not in result


def test_safe_parse_from_file_non_dict_returns_none(monkeypatch, capsys):
    monkeypatch.setattr(er.resumeparse, "read_file", lambda path: ["not", "a", "dict"])
    assert er.safe_parse_resume_from_file("x.pdf") is None
    assert "Error parsing resume file" in capsys.readouterr().out


def test_safe_parse_from_file_parser_raises_returns_none(monkeypatch):
    def boom(path):
        raise RuntimeError("parser exploded")

    monkeypatch.setattr(er.resumeparse, "read_file", boom)
    assert er.safe_parse_resume_from_file("x.pdf", idx=3) is None


# -------------------------------------------------
# safe_parse_resume (text variant)
# -------------------------------------------------

def test_safe_parse_text_cleans_values(monkeypatch):
    raw = {
        "skills": ["Java", None, 7],
        "name": "Te\\ud83dst",
        "total_exp": 2,
        "empty": None,
    }
    monkeypatch.setattr(er.resumeparse, "read_file", lambda path: raw)

    result = er.safe_parse_resume("some resume text", 0)
    assert result["skills"] == ["Java", 7]
    assert result["name"] == "Test"
    assert result["total_exp"] == 2
    assert "empty" not in result


def test_safe_parse_text_non_dict_returns_none(monkeypatch):
    monkeypatch.setattr(er.resumeparse, "read_file", lambda path: "nope")
    assert er.safe_parse_resume("text", 1) is None


def test_safe_parse_text_cleanup_swallows_unlink_error(monkeypatch):
    monkeypatch.setattr(er.resumeparse, "read_file", lambda path: {"ok": ["data"]})

    def failing_unlink(path):
        raise OSError("cannot remove")

    monkeypatch.setattr(er.os, "unlink", failing_unlink)

    # Should not raise even though cleanup fails in the finally block.
    result = er.safe_parse_resume("text", 2)
    assert result == {"ok": ["data"]}
