from unittest.mock import MagicMock

import pytest
import requests
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper


class DummyScraper(BaseScraper):
    """Concrete subclass so BaseScraper can be instantiated for testing."""

    def search_courses(self, query, limit=10):
        # Delegate to the abstract body so its line is executed.
        return super().search_courses(query, limit)

    def _parse_course_card(self, course_element):
        return super()._parse_course_card(course_element)


def test_init_uses_default_headers():
    scraper = DummyScraper('https://example.com')
    assert 'User-Agent' in scraper.headers
    assert scraper.base_url == 'https://example.com'


def test_init_uses_custom_headers():
    scraper = DummyScraper('https://example.com', headers={'X-Test': '1'})
    assert scraper.headers == {'X-Test': '1'}


def test_abstract_method_bodies_are_callable():
    scraper = DummyScraper('https://example.com')
    assert scraper.search_courses('q', 5) is None
    assert scraper._parse_course_card(None) is None


def test_make_request_success(monkeypatch):
    scraper = DummyScraper('https://example.com')
    monkeypatch.setattr('scrapers.base_scraper.time.sleep', lambda *a, **k: None)

    response = MagicMock()
    response.content = b"<html><body><p>hi</p></body></html>"
    response.raise_for_status = MagicMock()
    scraper.session = MagicMock()
    scraper.session.get.return_value = response

    soup = scraper._make_request('https://example.com/x', params={'a': 'b'})
    assert isinstance(soup, BeautifulSoup)
    assert soup.find('p').get_text() == 'hi'


def test_make_request_handles_request_exception(monkeypatch, capsys):
    scraper = DummyScraper('https://example.com')
    monkeypatch.setattr('scrapers.base_scraper.time.sleep', lambda *a, **k: None)
    scraper.session = MagicMock()
    scraper.session.get.side_effect = requests.RequestException('boom')

    assert scraper._make_request('https://example.com/x') is None
    assert 'Request failed' in capsys.readouterr().out


def test_extract_text_safely():
    scraper = DummyScraper('https://example.com')
    element = MagicMock()
    element.get_text.return_value = 'value'
    assert scraper._extract_text_safely(element) == 'value'
    assert scraper._extract_text_safely(None) == ''
    assert scraper._extract_text_safely(None, default='d') == 'd'


def test_extract_attribute_safely():
    scraper = DummyScraper('https://example.com')
    element = MagicMock()
    element.get.return_value = 'attr'
    assert scraper._extract_attribute_safely(element, 'href') == 'attr'
    assert scraper._extract_attribute_safely(None, 'href') == ''
    assert scraper._extract_attribute_safely(None, 'href', default='d') == 'd'


def test_standardize_relative_link_and_thumbnail():
    scraper = DummyScraper('https://example.com/')
    result = scraper._standardize_course_data(
        title='  Title  ',
        link='/learn/x',
        thumbnail='img/pic.png',
        instructor='  Inst  ',
        price=' Free ',
        rating=' 5 ',
    )
    assert result['title'] == 'Title'
    assert result['link'] == 'https://example.com/learn/x'
    assert result['thumbnail'] == 'https://example.com/img/pic.png'
    assert result['instructor'] == 'Inst'
    assert result['price'] == 'Free'
    assert result['rating'] == '5'


def test_standardize_absolute_link_and_protocol_relative_thumbnail():
    scraper = DummyScraper('https://example.com')
    result = scraper._standardize_course_data(
        title='T',
        link='https://other.com/x',
        thumbnail='//cdn.com/pic.png',
    )
    assert result['link'] == 'https://other.com/x'
    assert result['thumbnail'] == 'https://cdn.com/pic.png'


def test_standardize_absolute_thumbnail_and_empty_link():
    scraper = DummyScraper('https://example.com')
    result = scraper._standardize_course_data(
        title='T',
        link='',
        thumbnail='https://cdn.com/pic.png',
    )
    assert result['link'] == ''
    assert result['thumbnail'] == 'https://cdn.com/pic.png'
