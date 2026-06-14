from config import Config, get_platform_config, is_platform_enabled


def test_config_has_expected_attributes():
    assert isinstance(Config.DEBUG, bool)
    assert isinstance(Config.PORT, int)
    assert 'default_limit' in Config.SCRAPER_SETTINGS
    assert 'coursera' in Config.PLATFORM_CONFIGS
    assert 'youtube' in Config.PLATFORM_CONFIGS
    assert isinstance(Config.CORS_SETTINGS['origins'], list)
    assert Config.LOGGING_CONFIG['level']


def test_get_platform_config_known_platform():
    cfg = get_platform_config('Coursera')
    assert cfg['base_url'] == 'https://www.coursera.org'


def test_get_platform_config_unknown_platform_returns_empty():
    assert get_platform_config('does-not-exist') == {}


def test_is_platform_enabled_known_platform():
    # Coursera defaults to enabled.
    assert is_platform_enabled('coursera') is True


def test_is_platform_enabled_unknown_platform_returns_false():
    assert is_platform_enabled('nope') is False
