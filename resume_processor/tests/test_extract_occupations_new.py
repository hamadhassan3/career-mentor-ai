from scripts import extract_occupations_new as eon


def test_get_matching_occupations_returns_dicts():
    occupations = eon.get_matching_occupations()
    assert isinstance(occupations, list)
    assert len(occupations) > 0
    first = occupations[0]
    assert set(first.keys()) == {"code", "category", "name", "description"}
    # code is always empty in the new data; name and category are the job title.
    assert first["code"] == ""
    assert first["name"] == first["category"]


def test_get_matching_occupations_ignores_legacy_path_args():
    # The two path args are kept only for backwards compatibility and ignored.
    with_args = eon.get_matching_occupations("ignored1.csv", "ignored2.csv")
    without_args = eon.get_matching_occupations()
    assert with_args == without_args


def test_main_prints_summary(capsys):
    eon.main()
    out = capsys.readouterr().out
    assert "Total occupations:" in out
