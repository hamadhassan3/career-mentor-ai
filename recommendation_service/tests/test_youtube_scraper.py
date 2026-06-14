from unittest.mock import MagicMock

import pytest

from scrapers.youtube_scraper import YouTubeScraper


def test_init_requires_api_key(monkeypatch):
    monkeypatch.delenv('YOUTUBE_API_KEY', raising=False)
    with pytest.raises(ValueError):
        YouTubeScraper()


def test_init_with_api_key(monkeypatch):
    monkeypatch.setenv('YOUTUBE_API_KEY', 'abc')
    scraper = YouTubeScraper()
    assert scraper.api_key == 'abc'


def _make_scraper(monkeypatch):
    monkeypatch.setenv('YOUTUBE_API_KEY', 'abc')
    return YouTubeScraper()


def test_search_courses_success(monkeypatch):
    scraper = _make_scraper(monkeypatch)
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = {
        'items': [
            {
                'id': {'playlistId': 'PL123'},
                'snippet': {
                    'title': 'Python Course',
                    'channelTitle': 'Chan',
                    'description': 'desc',
                    'thumbnails': {'high': {'url': 'https://img/high.jpg'}},
                },
            }
        ]
    }
    monkeypatch.setattr('scrapers.youtube_scraper.requests.get', lambda *a, **k: response)

    courses = scraper.search_courses('python', limit=5)
    assert len(courses) == 1
    assert courses[0]['title'] == 'Python Course'
    assert courses[0]['link'] == 'https://www.youtube.com/playlist?list=PL123'
    assert courses[0]['instructor'] == 'Chan'
    assert courses[0]['price'] == 'Free'


def test_search_courses_no_items_key(monkeypatch):
    scraper = _make_scraper(monkeypatch)
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = {}
    monkeypatch.setattr('scrapers.youtube_scraper.requests.get', lambda *a, **k: response)
    assert scraper.search_courses('python') == []


def test_search_courses_skips_unparseable_items(monkeypatch):
    scraper = _make_scraper(monkeypatch)
    response = MagicMock()
    response.raise_for_status = MagicMock()
    # One valid item, one with no title (skipped -> _parse returns None).
    response.json.return_value = {
        'items': [
            {'id': {'playlistId': 'PL1'}, 'snippet': {'title': 'Ok'}},
            {'id': {}, 'snippet': {'title': ''}},
        ]
    }
    monkeypatch.setattr('scrapers.youtube_scraper.requests.get', lambda *a, **k: response)
    courses = scraper.search_courses('python')
    assert len(courses) == 1


def test_search_courses_handles_exception(monkeypatch, capsys):
    scraper = _make_scraper(monkeypatch)

    def boom(*a, **k):
        raise RuntimeError('network down')

    monkeypatch.setattr('scrapers.youtube_scraper.requests.get', boom)
    assert scraper.search_courses('python') == []
    assert 'Error searching YouTube' in capsys.readouterr().out


def test_parse_playlist_item_full(monkeypatch):
    scraper = _make_scraper(monkeypatch)
    item = {
        'id': {'playlistId': 'PL9'},
        'snippet': {
            'title': 'Title',
            'channelTitle': 'Chan',
            'thumbnails': {'medium': {'url': 'https://img/m.jpg'}},
        },
    }
    result = scraper._parse_playlist_item(item)
    assert result['link'] == 'https://www.youtube.com/playlist?list=PL9'
    assert result['thumbnail'] == 'https://img/m.jpg'


def test_parse_playlist_item_no_title_returns_none(monkeypatch):
    scraper = _make_scraper(monkeypatch)
    assert scraper._parse_playlist_item({'snippet': {'title': ''}}) is None


def test_parse_playlist_item_no_playlist_id(monkeypatch):
    scraper = _make_scraper(monkeypatch)
    result = scraper._parse_playlist_item({'id': {}, 'snippet': {'title': 'T'}})
    assert result['link'] == ''
    assert result['thumbnail'] == ''


def test_parse_playlist_item_handles_exception(monkeypatch):
    scraper = _make_scraper(monkeypatch)
    # snippet is a string -> .get() raises AttributeError -> None.
    assert scraper._parse_playlist_item({'snippet': 'not-a-dict'}) is None


def test_parse_course_card_returns_none(monkeypatch):
    scraper = _make_scraper(monkeypatch)
    assert scraper._parse_course_card(object()) is None


def test_make_request_override_returns_none(monkeypatch):
    scraper = _make_scraper(monkeypatch)
    assert scraper._make_request('https://x') is None
