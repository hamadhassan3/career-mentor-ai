from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import time
import random

class BaseScraper(ABC):
    def __init__(self, base_url: str, headers: Optional[Dict] = None):
        self.base_url = base_url
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _make_request(self, url: str, params: Optional[Dict] = None, delay: float = 1.0) -> Optional[BeautifulSoup]:
        try:
            time.sleep(random.uniform(0.5, delay))
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            return BeautifulSoup(response.content, 'html.parser')
            
        except requests.RequestException as e:
            print(f"Request failed for {url}: {str(e)}")
            return None
    
    def _extract_text_safely(self, element, default: str = "") -> str:
        if element:
            return element.get_text(strip=True)
        return default
    
    def _extract_attribute_safely(self, element, attribute: str, default: str = "") -> str:
        if element:
            return element.get(attribute, default)
        return default
    
    @abstractmethod
    def search_courses(self, query: str, limit: int = 10) -> List[Dict]:
        pass
    
    @abstractmethod
    def _parse_course_card(self, course_element) -> Optional[Dict]:
        pass
    
    def _standardize_course_data(self, title: str, link: str, thumbnail: str, 
                                instructor: str = "", price: str = "", rating: str = "") -> Dict:
        # Ensure proper URL formatting
        if link and not link.startswith('http'):
            link = f"{self.base_url.rstrip('/')}/{link.lstrip('/')}"
        
        if thumbnail and not thumbnail.startswith('http') and not thumbnail.startswith('//'):
            thumbnail = f"{self.base_url.rstrip('/')}/{thumbnail.lstrip('/')}"
        elif thumbnail and thumbnail.startswith('//'):
            thumbnail = f"https:{thumbnail}"
            
        return {
            'title': title.strip(),
            'link': link.strip(),
            'thumbnail': thumbnail.strip(),
            'instructor': instructor.strip(),
            'price': price.strip(),
            'rating': rating.strip()
        }