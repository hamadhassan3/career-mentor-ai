import builtins
import importlib
from unittest.mock import MagicMock

import pytest


def _scraper_returning(courses):
    scraper = MagicMock()
    scraper.search_courses.return_value = courses
    return scraper


def test_health_check(client):
    resp = client.get('/health')
    assert resp.status_code == 200
    body = resp.get_json()
    assert body['status'] == 'healthy'
    assert 'coursera' in body['available_platforms']


def test_get_platforms(client):
    resp = client.get('/platforms')
    assert resp.status_code == 200
    assert 'youtube' in resp.get_json()['platforms']


# --- /courses/coursera -------------------------------------------------------

def test_search_coursera_success(client, monkeypatch):
    monkeypatch.setattr(
        'app.ScraperFactory.get_scraper',
        lambda platform: _scraper_returning([{'title': 'C'}]),
    )
    resp = client.post('/courses/coursera', json={'query': 'python', 'limit': 3})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body['platform'] == 'coursera'
    assert body['total_results'] == 1
    assert body['courses'][0]['platform'] == 'coursera'


def test_search_coursera_missing_query(client):
    resp = client.post('/courses/coursera', json={'query': '  '})
    assert resp.status_code == 400
    assert resp.get_json()['error']


def test_search_coursera_internal_error(client, monkeypatch):
    def boom(platform):
        raise RuntimeError('fail')

    monkeypatch.setattr('app.ScraperFactory.get_scraper', boom)
    resp = client.post('/courses/coursera', json={'query': 'python'})
    assert resp.status_code == 500
    assert resp.get_json()['error'] == 'Internal server error'


# --- /courses/youtube --------------------------------------------------------

def test_search_youtube_success(client, monkeypatch):
    monkeypatch.setattr(
        'app.ScraperFactory.get_scraper',
        lambda platform: _scraper_returning([{'title': 'Y'}]),
    )
    resp = client.post('/courses/youtube', json={'query': 'python'})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body['platform'] == 'youtube'
    assert body['courses'][0]['platform'] == 'youtube'


def test_search_youtube_missing_query(client):
    resp = client.post('/courses/youtube', json={'query': ''})
    assert resp.status_code == 400


def test_search_youtube_internal_error(client, monkeypatch):
    def boom(platform):
        raise RuntimeError('fail')

    monkeypatch.setattr('app.ScraperFactory.get_scraper', boom)
    resp = client.post('/courses/youtube', json={'query': 'python'})
    assert resp.status_code == 500


# --- /courses/search ---------------------------------------------------------

def test_search_courses_success(client, monkeypatch):
    monkeypatch.setattr(
        'app.ScraperFactory.get_scraper',
        lambda platform: _scraper_returning([{'title': f'{platform}-1'}, {'title': f'{platform}-2'}]),
    )
    resp = client.post('/courses/search', json={'query': 'python'})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body['platforms_searched'] == ['coursera', 'youtube']
    assert body['platform_breakdown']['coursera']['count'] == 2
    assert body['total_results'] == 4


def test_search_courses_uses_limit_for_unknown_platform_cap(client, monkeypatch):
    monkeypatch.setattr(
        'app.ScraperFactory.get_scraper',
        lambda platform: _scraper_returning([{'title': 'x'}]),
    )
    resp = client.post('/courses/search', json={'query': 'python', 'platforms': ['edx'], 'limit': 5})
    assert resp.status_code == 200
    assert resp.get_json()['platform_breakdown']['edx']['count'] == 1


def test_search_courses_missing_query(client):
    resp = client.post('/courses/search', json={'query': ''})
    assert resp.status_code == 400


def test_search_courses_per_platform_error(client, monkeypatch):
    def boom(platform):
        raise RuntimeError('platform down')

    monkeypatch.setattr('app.ScraperFactory.get_scraper', boom)
    resp = client.post('/courses/search', json={'query': 'python', 'platforms': ['coursera']})
    assert resp.status_code == 200
    breakdown = resp.get_json()['platform_breakdown']['coursera']
    assert breakdown['count'] == 0
    assert breakdown['error'] == 'platform down'


def test_search_courses_internal_error(client):
    # A non-iterable "platforms" value triggers the outer exception handler.
    resp = client.post('/courses/search', json={'query': 'python', 'platforms': 123})
    assert resp.status_code == 500
    assert resp.get_json()['error'] == 'Internal server error'


# --- dotenv import fallback --------------------------------------------------

def test_app_handles_missing_dotenv(monkeypatch):
    """Reload app with `dotenv` import forced to fail to cover the fallback."""
    import app

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == 'dotenv':
            raise ImportError('no dotenv')
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, '__import__', fake_import)
    reloaded = importlib.reload(app)
    assert reloaded.app is not None
    # Restore the normally-imported module for any later tests.
    monkeypatch.undo()
    importlib.reload(app)
