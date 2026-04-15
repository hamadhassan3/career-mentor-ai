from typing import List, Dict, Optional
from .base_scraper import BaseScraper

class UdemyScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            base_url="https://www.udemy.com",
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            }
        )
    
    def search_courses(self, query: str, limit: int = 10) -> List[Dict]:
        search_url = f"{self.base_url}/courses/search/"
        params = {'q': query}
        
        soup = self._make_request(search_url, params=params)
        if not soup:
            return []
        
        courses = []
        course_cards = soup.find_all('div', {'data-purpose': 'course-card-container'})
        
        if not course_cards:
            course_cards = soup.find_all('a', href=lambda x: x and '/course/' in x)
        
        for card in course_cards[:limit]:
            course_data = self._parse_course_card(card)
            if course_data:
                courses.append(course_data)
        
        return courses[:limit]
    
    def _parse_course_card(self, course_element) -> Optional[Dict]:
        try:
            # Check if course_element itself is a link
            if course_element.name == 'a' and course_element.get('href'):
                link_elem = course_element
                title_elem = course_element
            else:
                title_elem = (
                    course_element.find('h3', {'data-purpose': 'course-title-url'}) or
                    course_element.find('h3')
                )
                link_elem = (
                    course_element.find('a', {'data-purpose': 'course-title-url'}) or
                    course_element.find('a', href=lambda x: x and '/course/' in x) or
                    course_element.find('a', href=True)
                )
            
            if not title_elem:
                return None
            
            title = self._extract_text_safely(title_elem)
            if not title:
                return None
            
            link = ""
            if link_elem:
                href = link_elem.get('href', '')
                if href.startswith('/'):
                    link = f"{self.base_url}{href}"
                else:
                    link = href
            
            img = course_element.find('img', {'data-purpose': 'course-image'})
            if not img:
                img = course_element.find('img')
            thumbnail = img.get('src', '') if img else ''
            
            instructor_elem = course_element.find('span', {'data-purpose': 'instructor-name'})
            instructor = self._extract_text_safely(instructor_elem)
            
            price_elem = course_element.find('span', {'data-purpose': 'course-price-text'})
            price = self._extract_text_safely(price_elem)
            
            return self._standardize_course_data(
                title=title,
                link=link,
                thumbnail=thumbnail,
                instructor=instructor,
                price=price,
                rating=""
            )
            
        except Exception:
            return None