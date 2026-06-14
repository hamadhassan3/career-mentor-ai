import pytest
from bs4 import BeautifulSoup

from scrapers.coursera_scraper import CourseraScraper


def soup(html):
    return BeautifulSoup(html, 'html.parser')


def test_search_courses_returns_empty_when_no_soup(monkeypatch):
    scraper = CourseraScraper()
    monkeypatch.setattr(scraper, '_make_request', lambda *a, **k: None)
    assert scraper.search_courses('python') == []


def test_search_courses_parses_product_cards(monkeypatch):
    scraper = CourseraScraper()
    html = """
    <div data-testid="product-card-cds">
        <h3 class="cds-CommonCard-title">Intro to Python</h3>
        <a class="cds-CommonCard-titleLink" href="/learn/python">link</a>
        <img src="https://img/pic.jpg"/>
        <p class="cds-ProductCard-partnerNames">Coursera Inc</p>
    </div>
    """
    monkeypatch.setattr(scraper, '_make_request', lambda *a, **k: soup(html))
    courses = scraper.search_courses('python', limit=10)
    assert len(courses) == 1
    assert courses[0]['title'] == 'Intro to Python'
    assert courses[0]['link'] == 'https://www.coursera.org/learn/python'
    assert courses[0]['instructor'] == 'Coursera Inc'


def test_search_courses_anchor_fallback(monkeypatch):
    scraper = CourseraScraper()
    html = '<a href="/learn/ml">Machine Learning</a>'
    monkeypatch.setattr(scraper, '_make_request', lambda *a, **k: soup(html))
    courses = scraper.search_courses('ml')
    assert len(courses) == 1
    assert courses[0]['title'] == 'Machine Learning'
    assert courses[0]['link'] == 'https://www.coursera.org/learn/ml'


def test_search_courses_no_cards(monkeypatch):
    scraper = CourseraScraper()
    monkeypatch.setattr(scraper, '_make_request', lambda *a, **k: soup('<div></div>'))
    assert scraper.search_courses('python') == []


def test_parse_course_card_anchor_with_http_link():
    scraper = CourseraScraper()
    element = soup('<a href="https://www.coursera.org/learn/x">Course X</a>').find('a')
    result = scraper._parse_course_card(element)
    assert result['title'] == 'Course X'
    assert result['link'] == 'https://www.coursera.org/learn/x'


def test_parse_course_card_no_title_returns_none():
    scraper = CourseraScraper()
    element = soup('<div><span>nothing here</span></div>').find('div')
    assert scraper._parse_course_card(element) is None


def test_parse_course_card_empty_title_returns_none():
    scraper = CourseraScraper()
    element = soup('<div><h3 class="cds-CommonCard-title"></h3></div>').find('div')
    assert scraper._parse_course_card(element) is None


def test_parse_course_card_without_image():
    scraper = CourseraScraper()
    html = '<div><h3>Title</h3><a href="/learn/x">l</a></div>'
    element = soup(html).find('div')
    result = scraper._parse_course_card(element)
    assert result['thumbnail'] == ''
    assert result['link'] == 'https://www.coursera.org/learn/x'


def test_parse_course_card_handles_exception():
    scraper = CourseraScraper()
    # None has no .name attribute -> AttributeError -> None.
    assert scraper._parse_course_card(None) is None


def test_clean_thumbnail_url_empty():
    scraper = CourseraScraper()
    assert scraper._clean_thumbnail_url('') == ''


def test_clean_thumbnail_url_removes_unwanted_params():
    scraper = CourseraScraper()
    cleaned = scraper._clean_thumbnail_url('https://img/pic.jpg?blur=200&px=5&w=300')
    assert 'blur' not in cleaned
    assert 'px=' not in cleaned
    assert 'w=300' in cleaned


def test_clean_thumbnail_url_handles_exception():
    scraper = CourseraScraper()
    # A non-string (but truthy) value makes urlparse raise -> original returned.
    sentinel = 12345
    assert scraper._clean_thumbnail_url(sentinel) == sentinel
