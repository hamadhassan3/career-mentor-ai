import pytest

import scripts.clean_designations_new as cdn


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def test_normalize():
    assert cdn.normalize("  Senior DEV  ") == "senior dev"


def test_similarity():
    assert cdn.similarity("manager", "manager") == 1.0


# -------------------------------------------------
# Loaders
# -------------------------------------------------

def test_load_occupation_titles_real_data():
    titles, lookup = cdn.load_occupation_titles()
    assert len(titles) > 0
    sample = lookup[titles[0]]
    assert sample["type"] == "designation"
    assert sample["standardized_name"]


def test_load_ml_trained_designations_real_data():
    titles, lookup = cdn.load_ml_trained_designations()
    assert len(titles) > 0
    assert lookup[titles[0]]["type"] == "ml_designation"


def test_load_ml_trained_designations_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        cdn.load_ml_trained_designations(data_dir=tmp_path)


# -------------------------------------------------
# find_best_designation_match
# -------------------------------------------------

DEV_LOOKUP = {
    "python developer": {"standardized_name": "Python Developer", "code": "", "category": "Python Developer"}
}


def test_match_too_short():
    assert cdn.find_best_designation_match("ab", ["python developer"], DEV_LOOKUP) is None


def test_match_direct():
    match = cdn.find_best_designation_match("Python Developer", ["python developer"], DEV_LOOKUP)
    assert match["standardized_name"] == "Python Developer"


def test_match_containment():
    lookup = {"developer": {"standardized_name": "Developer", "code": "", "category": "Developer"}}
    match = cdn.find_best_designation_match("senior developer engineer", ["developer"], lookup)
    assert match["standardized_name"] == "Developer"


def test_match_similarity():
    lookup = {"data scientist": {"standardized_name": "Data Scientist", "code": "", "category": "Data Scientist"}}
    match = cdn.find_best_designation_match("data scientyst", ["data scientist"], lookup)
    assert match["standardized_name"] == "Data Scientist"


# -------------------------------------------------
# clean_designations
# -------------------------------------------------

def test_clean_designations_non_list():
    assert cdn.clean_designations("not a list") == ([], [], [])


def test_clean_designations_filters_and_dedupes():
    # Pick a real, letters-only job title so it matches directly against the data file.
    titles, lookup = cdn.load_occupation_titles()
    real_title = next(
        lookup[t]["standardized_name"]
        for t in titles
        if all(c.isalpha() or c.isspace() for c in t)
    )

    designation_list = [
        None,            # falsy -> skipped
        9999,            # non-str -> skipped
        "ab",            # too short -> skipped
        "x" * 90,        # too long -> skipped
        "ltd",           # noise -> skipped
        real_title,      # valid -> matched
        real_title,      # duplicate -> deduped
    ]

    cleaned, codes, categories = cdn.clean_designations(designation_list)
    assert cleaned == [real_title]
    assert codes == [""]
    assert categories == [real_title]


def test_main_prints(capsys):
    cdn.main()
    out = capsys.readouterr().out
    assert out.strip() != ""
