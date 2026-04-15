from typing import Dict, Type
from .base_scraper import BaseScraper
from .coursera_scraper import CourseraScraper
from .youtube_scraper import YouTubeScraper

class ScraperFactory:
    _scrapers: Dict[str, Type[BaseScraper]] = {
        'coursera': CourseraScraper,
        'youtube': YouTubeScraper,
    }
    
    @classmethod
    def register_scraper(cls, platform_name: str, scraper_class: Type[BaseScraper]):
        cls._scrapers[platform_name.lower()] = scraper_class
    
    @classmethod
    def get_scraper(cls, platform_name: str) -> BaseScraper:
        platform_name = platform_name.lower()
        
        if platform_name not in cls._scrapers:
            raise ValueError(f"Unsupported platform: {platform_name}. Supported platforms: {list(cls._scrapers.keys())}")
        
        return cls._scrapers[platform_name]()
    
    @classmethod
    def get_available_platforms(cls) -> list:
        return list(cls._scrapers.keys())
    
    @classmethod
    def is_platform_supported(cls, platform_name: str) -> bool:
        return platform_name.lower() in cls._scrapers