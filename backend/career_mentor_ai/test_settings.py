"""
Test settings: run the suite against a fast in-memory SQLite database and
deterministic, offline-friendly defaults so unit tests never touch Postgres,
S3, SMTP, or any external LLM/recommendation service.
"""
import os

# Provide harmless defaults BEFORE the base settings import so module-level
# os.getenv() calls (SECRET_KEY, email, AWS, etc.) resolve to safe values.
os.environ.setdefault('SECRET_KEY', 'test-secret-key-not-for-production')
os.environ.setdefault('DEBUG', 'False')
os.environ.setdefault('DEFAULT_FROM_EMAIL', 'noreply@test.local')
os.environ.setdefault('AWS_ACCESS_KEY_ID', 'test-access-key')
os.environ.setdefault('AWS_SECRET_ACCESS_KEY', 'test-secret-key')
os.environ.setdefault('AWS_S3_BUCKET_NAME', 'test-bucket')

from career_mentor_ai.settings import *  # noqa: F401,F403,E402

# Fast, in-memory database — no Postgres required.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Fast password hashing keeps auth-heavy tests snappy.
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# Collect emails in memory instead of sending them over SMTP.
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Deterministic value used by password-reset link assertions.
FRONTEND_URL = 'http://testserver'
