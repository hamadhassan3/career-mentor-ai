import scripts.clean_skills_new as csn


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def test_normalize_lowercases_and_strips():
    assert csn.normalize("  PyThon  ") == "python"


def test_similarity_identical_and_different():
    assert csn.similarity("python", "python") == 1.0
    assert csn.similarity("python", "java") < 0.5


# -------------------------------------------------
# Real data loaders
# -------------------------------------------------

def test_load_technology_skills_real_data():
    skills, lookup = csn.load_technology_skills()
    assert len(skills) > 0
    sample = lookup[skills[0]]
    assert sample["skill_type"] == "technical"
    assert sample["hot_technology"] is False


def test_load_soft_skills_real_data():
    skills, lookup = csn.load_soft_skills()
    assert len(skills) > 0
    assert lookup[skills[0]]["category"] == "Soft Skill"


def test_load_language_skills_real_data():
    languages, lookup = csn.load_language_skills()
    assert len(languages) > 0
    sample = lookup[languages[0]]
    assert sample["category"] == "language"
    assert "iso_code" in sample


# -------------------------------------------------
# find_best_skill_match
# -------------------------------------------------

PY_LOOKUP = {"python": {"standardized_name": "Python", "category": "Lang"}}


def test_find_best_skill_match_too_short():
    assert csn.find_best_skill_match("a", ["python"], PY_LOOKUP) is None


def test_find_best_skill_match_two_char_non_whitelisted():
    assert csn.find_best_skill_match("zz", ["python"], PY_LOOKUP) is None


def test_find_best_skill_match_direct():
    assert csn.find_best_skill_match("Python", ["python"], PY_LOOKUP)["standardized_name"] == "Python"


def test_find_best_skill_match_skips_single_char_and_matches_similar():
    lookup = {
        "x": {"standardized_name": "X", "category": "noise"},
        "python": {"standardized_name": "Python", "category": "Lang"},
    }
    match = csn.find_best_skill_match("pythonn", ["x", "python"], lookup)
    assert match["standardized_name"] == "Python"


# -------------------------------------------------
# find_best_soft_skill_match
# -------------------------------------------------

def test_find_best_soft_skill_match_too_short():
    assert csn.find_best_soft_skill_match("ab", ["teamwork"], {}) is None


def test_find_best_soft_skill_match_direct():
    lookup = {"teamwork": {"standardized_name": "Teamwork", "category": "Soft Skill"}}
    assert csn.find_best_soft_skill_match("Teamwork", ["teamwork"], lookup)["standardized_name"] == "Teamwork"


def test_find_best_soft_skill_match_similar_single_word():
    lookup = {
        "leadership": {"standardized_name": "Leadership", "category": "Soft Skill"},
        "team work": {"standardized_name": "Team Work", "category": "Soft Skill"},
    }
    match = csn.find_best_soft_skill_match("leadrship", ["leadership", "team work"], lookup)
    assert match["standardized_name"] == "Leadership"


# -------------------------------------------------
# find_best_language_match
# -------------------------------------------------

EN_LOOKUP = {"english": {"standardized_name": "English", "category": "language"}}


def test_find_best_language_match_too_short():
    assert csn.find_best_language_match("ab", ["english"], EN_LOOKUP) is None


def test_find_best_language_match_direct():
    assert csn.find_best_language_match("English", ["english"], EN_LOOKUP)["standardized_name"] == "English"


def test_find_best_language_match_whole_word_containment():
    match = csn.find_best_language_match("english speaking", ["english"], EN_LOOKUP)
    assert match["standardized_name"] == "English"


def test_find_best_language_match_similarity():
    lookup = {"spanish": {"standardized_name": "Spanish", "category": "language"}}
    match = csn.find_best_language_match("spanis", ["spanish"], lookup)
    assert match["standardized_name"] == "Spanish"


# -------------------------------------------------
# clean_skills
# -------------------------------------------------

def test_clean_skills_non_list_returns_six_empty():
    assert csn.clean_skills("not a list") == ([], [], [], [], [], [])


def test_clean_skills_routes_each_bucket(monkeypatch):
    lang = {"standardized_name": "English", "category": "language"}
    it = {"standardized_name": "Python", "category": "Backend"}
    soft = {"standardized_name": "Teamwork", "category": "Soft Skill"}

    monkeypatch.setattr(
        csn, "find_best_language_match",
        lambda skill, *a, **k: lang if skill in ("lang1", "lang1 ") else None,
    )
    monkeypatch.setattr(
        csn, "find_best_skill_match",
        lambda skill, *a, **k: it if skill in ("it1",) else None,
    )
    monkeypatch.setattr(
        csn, "find_best_soft_skill_match",
        lambda skill, *a, **k: soft if skill in ("soft1",) else None,
    )

    skills_list = [
        None,            # falsy -> skipped
        12345,           # non-str -> skipped
        "a",             # too short -> skipped
        "x" * 60,        # too long -> skipped
        "ltd",           # noise -> skipped
        "z",             # single char not r/c -> skipped
        "r",             # single char allowed, matches nothing
        "lang1",         # -> language bucket
        "lang1",         # duplicate language -> deduped
        "it1",           # -> IT bucket
        "it1",           # duplicate IT -> deduped
        "soft1",         # -> soft bucket
        "nomatch",       # matches nothing
    ]

    it_skills, it_cats, soft_skills, soft_cats, langs, lang_cats = csn.clean_skills(skills_list)

    assert it_skills == ["Python"] and it_cats == ["Backend"]
    assert soft_skills == ["Teamwork"] and soft_cats == ["Soft Skill"]
    assert langs == ["English"] and lang_cats == ["language"]
