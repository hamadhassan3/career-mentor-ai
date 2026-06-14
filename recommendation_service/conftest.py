import os

# Ensure the YouTube scraper can be instantiated during tests without a real key.
os.environ.setdefault('YOUTUBE_API_KEY', 'test-key')

import pytest

from app import app as flask_app


@pytest.fixture
def client():
    """Flask test client for exercising the HTTP routes."""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as test_client:
        yield test_client
