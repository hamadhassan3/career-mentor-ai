import pickle
from unittest import mock

import numpy as np

# Force these heavy modules (imported lazily inside the /predict_next_skill route)
# into sys.modules now, so patching builtins.open in the tests below does not
# corrupt their import machinery.
import pandas  # noqa: F401
import xgboost  # noqa: F401


# =================================================
# /predict  (LSTM next-skill model)
# =================================================

class _FakeTok:
    def __init__(self, word_index, sequences):
        self.word_index = word_index
        self._sequences = sequences

    def texts_to_sequences(self, texts):
        return self._sequences


class _FakeModel:
    def __init__(self, it_pred, soft_pred):
        self._it = it_pred
        self._soft = soft_pred

    def predict(self, inputs):
        return self._it, self._soft


def _wire_predict(monkeypatch, app_mod, *, it_pred, soft_pred, des_seq):
    monkeypatch.setattr(app_mod, "it_tokenizer", _FakeTok({"python": 1, "java": 2, "sql": 3}, [[1, 2]]))
    monkeypatch.setattr(app_mod, "soft_tokenizer", _FakeTok({"teamwork": 1}, [[1]]))
    monkeypatch.setattr(app_mod, "des_tokenizer", _FakeTok({}, des_seq))
    monkeypatch.setattr(app_mod, "it_index_word", {1: "python", 2: "java", 3: "sql"})
    monkeypatch.setattr(app_mod, "soft_index_word", {1: "teamwork", 2: "leadership"})
    monkeypatch.setattr(app_mod, "model", _FakeModel(np.array([it_pred]), np.array([soft_pred])))


def test_predict_high_confidence_excludes_current(client, app_mod, monkeypatch):
    # max IT score 0.9 -> high-confidence (low) threshold branch.
    _wire_predict(
        monkeypatch, app_mod,
        it_pred=[0.0, 0.9, 0.5, 0.001],   # python=0.9 kept, java excluded (current), sql below threshold
        soft_pred=[0.0, 0.4, 0.9],        # teamwork excluded (current), leadership kept
        des_seq=[[2]],                    # non-empty designation sequence
    )

    resp = client.post("/predict", json={
        "it_skill_categories": ["Java", "Cobol"],   # java known, cobol absent from tokenizer
        "soft_skills": ["Teamwork"],
        "desired_designation": "Backend Engineer",
    })

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["predicted_next_it_skills"] == ["python"]
    assert body["predicted_next_soft_skills"] == ["leadership"]
    assert "exclude" in body["note"]


def test_predict_medium_and_low_thresholds_empty_designation(client, app_mod, monkeypatch):
    # IT max 0.1 -> medium threshold; soft max 0.01 -> low-confidence threshold.
    _wire_predict(
        monkeypatch, app_mod,
        it_pred=[0.0, 0.1, 0.0, 0.0],
        soft_pred=[0.0, 0.01, 0.0],
        des_seq=[[]],                     # empty designation sequence -> X_des = [[0]]
    )

    resp = client.post("/predict", json={
        "it_skill_categories": ["Python", "  "],   # blank entry filtered by `if s.strip()`
        "soft_skills": [],
        "desired_designation": "",
    })

    assert resp.status_code == 200
    body = resp.get_json()
    assert isinstance(body["predicted_next_it_skills"], list)
    assert isinstance(body["predicted_next_soft_skills"], list)


def test_predict_handles_exception(client, app_mod, monkeypatch):
    boom = _FakeModel(None, None)
    monkeypatch.setattr(boom, "predict", mock.Mock(side_effect=RuntimeError("model down")))
    monkeypatch.setattr(app_mod, "it_tokenizer", _FakeTok({}, [[]]))
    monkeypatch.setattr(app_mod, "soft_tokenizer", _FakeTok({}, [[]]))
    monkeypatch.setattr(app_mod, "des_tokenizer", _FakeTok({}, [[]]))
    monkeypatch.setattr(app_mod, "model", boom)

    resp = client.post("/predict", json={"it_skill_categories": [], "soft_skills": [], "desired_designation": ""})
    assert resp.status_code == 500
    assert "model down" in resp.get_json()["error"]


# =================================================
# /predict_next_skill  (XGBoost model)
# =================================================

def _model_data():
    xgb_model = mock.Mock()
    # 12 classes so the "top 10 new skills" break is exercised.
    probs = np.linspace(0.95, 0.1, 12)
    xgb_model.predict.return_value = np.array([probs])

    label_encoder = mock.Mock()
    labels = [f"IT_SKILL{i}" for i in range(11)] + ["SOFT_TEAMWORK"]
    label_encoder.inverse_transform.return_value = np.array(labels)

    feature_columns = [
        "has_it_python", "has_it_java",
        "has_soft_teamwork",
        "prof_developer",
        "it_skill_count", "soft_skill_count", "total_skill_count",
        "int_prof_developer_has_it_python",  # interaction present -> exercised
        "extra_unseen_column",               # forces the "add missing column" branch
    ]
    return {
        "xgboost_model": xgb_model,
        "label_encoder": label_encoder,
        "feature_columns": feature_columns,
        "all_skills": {"python", "java"},
        "all_soft_skills": {"teamwork"},
        "all_professions": {"developer"},
    }


def test_predict_next_skill_success(client):
    md = _model_data()
    with mock.patch("builtins.open", mock.mock_open(read_data=b"x")), \
         mock.patch.object(pickle, "load", return_value=md), \
         mock.patch("xgboost.DMatrix", return_value=mock.Mock()):
        resp = client.post("/predict_next_skill", json={
            "it_skill_categories": ["python"],
            "soft_skills": [],
            "desired_designation": "developer",
        })

    assert resp.status_code == 200
    body = resp.get_json()
    assert body["best_next_skill"] is not None
    assert len(body["top_3_skills"]) == 10
    assert {"skill", "type", "confidence"} <= set(body["best_next_skill"].keys())


def test_predict_next_skill_model_file_missing(client):
    with mock.patch("builtins.open", side_effect=FileNotFoundError):
        resp = client.post("/predict_next_skill", json={
            "it_skill_categories": ["python"],
            "soft_skills": [],
            "desired_designation": "developer",
        })
    assert resp.status_code == 500
    assert "model not found" in resp.get_json()["error"].lower()


def test_predict_next_skill_unexpected_error(client):
    # A corrupt pickle payload raises inside the body -> generic 500 handler.
    with mock.patch("builtins.open", mock.mock_open(read_data=b"x")), \
         mock.patch.object(pickle, "load", side_effect=ValueError("bad pickle")):
        resp = client.post("/predict_next_skill", json={
            "it_skill_categories": ["python"],
            "soft_skills": [],
            "desired_designation": "developer",
        })
    assert resp.status_code == 500
    assert "bad pickle" in resp.get_json()["error"]
