import os
from typing import Dict, Any

class Config:
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    SCRAPER_SETTINGS = {
        'default_limit': int(os.environ.get('DEFAULT_COURSE_LIMIT', 10)),
        'max_limit': int(os.environ.get('MAX_COURSE_LIMIT', 50)),
        'request_delay': float(os.environ.get('REQUEST_DELAY', 1.0)),
        'request_timeout': int(os.environ.get('REQUEST_TIMEOUT', 10)),
        'retry_attempts': int(os.environ.get('RETRY_ATTEMPTS', 3)),
    }
    
    PLATFORM_CONFIGS = {
        'coursera': {
            'enabled': os.environ.get('COURSERA_ENABLED', 'True').lower() == 'true',
            'base_url': 'https://www.coursera.org',
            'search_endpoint': '/search',
            'rate_limit': 1.5,
        },
        'udemy': {
            'enabled': os.environ.get('UDEMY_ENABLED', 'True').lower() == 'true',
            'base_url': 'https://www.udemy.com',
            'search_endpoint': '/courses/search/',
            'rate_limit': 1.0,
        }
    }
    
    CORS_SETTINGS = {
        'origins': os.environ.get('CORS_ORIGINS', '*').split(','),
        'methods': ['GET', 'POST', 'OPTIONS'],
        'allow_headers': ['Content-Type', 'Authorization']
    }
    
    LOGGING_CONFIG = {
        'level': os.environ.get('LOG_LEVEL', 'INFO').upper(),
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    }

def get_platform_config(platform: str) -> Dict[str, Any]:
    return Config.PLATFORM_CONFIGS.get(platform.lower(), {})

def is_platform_enabled(platform: str) -> bool:
    platform_config = get_platform_config(platform)
    return platform_config.get('enabled', False)