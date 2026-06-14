import pytest

from scrapers.base_scraper import BaseScraper
from scrapers.coursera_scraper import CourseraScraper
from scrapers.youtube_scraper import YouTubeScraper
from scrapers.scraper_factory import ScraperFactory


def test_get_scraper_coursera():
    assert isinstance(ScraperFactory.get_scraper('Coursera'), CourseraScraper)


def test_get_scraper_youtube():
    assert isinstance(ScraperFactory.get_scraper('youtube'), YouTubeScraper)


def test_get_scraper_unsupported_raises():
    with pytest.raises(ValueError) as exc:
        ScraperFactory.get_scraper('myspace')
    assert 'Unsupported platform' in str(exc.value)


def test_get_available_platforms():
    platforms = ScraperFactory.get_available_platforms()
    assert 'coursera' in platforms
    assert 'youtube' in platforms


def test_is_platform_supported():
    assert ScraperFactory.is_platform_supported('Coursera') is True
    assert ScraperFactory.is_platform_supported('unknown') is False


def test_register_scraper():
    class FakeScraper(BaseScraper):
        def __init__(self):
            super().__init__('https://fake.test')

        def search_courses(self, query, limit=10):
            return []

        def _parse_course_card(self, course_element):
            return None

    try:
        ScraperFactory.register_scraper('Fake', FakeScraper)
        assert ScraperFactory.is_platform_supported('fake') is True
        assert isinstance(ScraperFactory.get_scraper('fake'), FakeScraper)
    finally:
        ScraperFactory._scrapers.pop('fake', None)
