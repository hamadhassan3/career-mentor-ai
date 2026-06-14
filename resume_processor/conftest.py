"""Shared pytest fixtures and import-time stubs for the resume_processor service.

``app.py`` pulls in TensorFlow/Keras and loads a Keras model, several tokenizers
and a config file the moment it is imported. Loading the real ML stack would make
the suite slow and non-deterministic, so we register lightweight stand-ins in
``sys.modules`` *before* importing ``app``. The data-loading helpers (which read
the small CSV/JSON files under ``scripts/data``) are left untouched and run for
real, so the GET endpoints return realistic payloads.
"""

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _install_fake_tensorflow():
    """Register fake ``tensorflow`` modules so importing app.py is fast."""

    def _module(name):
        mod = types.ModuleType(name)
        sys.modules[name] = mod
        return mod

    tf = _module("tensorflow")
    tf.config = types.SimpleNamespace(
        list_physical_devices=lambda kind: [],
        experimental=types.SimpleNamespace(set_memory_growth=lambda *a, **k: None),
    )

    keras = _module("tensorflow.keras")
    tf.keras = keras

    models = _module("tensorflow.keras.models")
    models.load_model = lambda path: MagicMock(name="keras_model")
    keras.models = models

    preprocessing = _module("tensorflow.keras.preprocessing")
    keras.preprocessing = preprocessing

    text = _module("tensorflow.keras.preprocessing.text")

    def _tokenizer_from_json(blob):
        tok = MagicMock(name="tokenizer")
        tok.word_index = {}
        tok.texts_to_sequences = lambda seqs: [[] for _ in seqs]
        return tok

    text.tokenizer_from_json = _tokenizer_from_json
    preprocessing.text = text

    sequence = _module("tensorflow.keras.preprocessing.sequence")

    def _pad_sequences(seqs, maxlen=None, padding="post"):
        padded = []
        for seq in seqs:
            seq = list(seq)[:maxlen]
            if maxlen:
                seq = seq + [0] * (maxlen - len(seq))
            padded.append(seq)
        return np.array(padded)

    sequence.pad_sequences = _pad_sequences
    preprocessing.sequence = sequence


_install_fake_tensorflow()

import app as app_module  # noqa: E402  (must follow the fake-tensorflow install)


@pytest.fixture
def app_mod():
    """The imported ``app`` module, for poking at module-level globals."""
    return app_module


@pytest.fixture
def client():
    """Flask test client for exercising the HTTP routes."""
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
        yield test_client
