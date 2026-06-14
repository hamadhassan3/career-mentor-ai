"""Cover the module-level initialization branches in app.py.

These require re-importing ``app`` under patched conditions, so each test
reloads the module inside a patch context and then reloads it once more to
restore the clean (happy-path) state for the rest of the suite.
"""

import importlib
import sys
from unittest import mock

import app as app_module


def _restore():
    importlib.reload(app_module)


def test_data_loader_failures_fall_back_to_empty_lists():
    def boom(*args, **kwargs):
        raise RuntimeError("data load failed")

    patches = [
        mock.patch("scripts.clean_skills_new.load_technology_skills", side_effect=boom),
        mock.patch("scripts.clean_skills_new.load_soft_skills", side_effect=boom),
        mock.patch("scripts.clean_skills_new.load_language_skills", side_effect=boom),
        mock.patch("scripts.clean_designations_new.load_ml_trained_designations", side_effect=boom),
        mock.patch("scripts.extract_occupations_new.get_matching_occupations", side_effect=boom),
    ]
    try:
        for p in patches:
            p.start()
        importlib.reload(app_module)

        assert app_module.skills == []
        assert app_module.designations == []
        assert app_module.it_categories == []
        assert app_module.languages == []
        assert app_module.soft_skills_list == []
    finally:
        for p in patches:
            p.stop()
        _restore()

    # After restoring, real data is loaded again.
    assert len(app_module.skills) > 0


def test_gpu_memory_growth_branch_handles_runtime_error():
    tf = sys.modules["tensorflow"]
    fake_device = object()

    with mock.patch.object(tf.config, "list_physical_devices", return_value=[fake_device]), \
         mock.patch.object(
             tf.config.experimental, "set_memory_growth",
             side_effect=RuntimeError("GPUs already initialized"),
         ):
        try:
            # Should import cleanly despite the GPU configuration raising.
            importlib.reload(app_module)
            assert app_module.app is not None
        finally:
            _restore()
