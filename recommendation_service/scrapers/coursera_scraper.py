from typing import List, Dict, Optional
from .base_scraper import BaseScraper

class CourseraScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            base_url="https://www.coursera.org",
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            }
        )
    
    def search_courses(self, query: str, limit: int = 10) -> List[Dict]:
        search_url = f"{self.base_url}/search"
        params = {
            'query': query,
            'index': 'prod_all_launched_products_term_optimization'
        }
        
        soup = self._make_request(search_url, params=params)
        if not soup:
            return []
        
        courses = []
        course_cards = (
            soup.find_all('div', {'data-testid': 'product-card-cds'}) or
            soup.find_all('div', class_=lambda x: x and 'cds-ProductCard-base' in str(x)) or
            soup.find_all('li', class_=lambda x: x and 'cds-9' in str(x) and 'cds-grid-item' in str(x))
        )
        
        if not course_cards:
            course_cards = soup.find_all('a', href=lambda x: x and ('/learn/' in x or '/specializations/' in x))
        
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
                    course_element.find('h3', class_='cds-CommonCard-title') or
                    course_element.find('a', class_=lambda x: x and 'cds-CommonCard-titleLink' in str(x)) or
                    course_element.find('h3') or
                    course_element.find('h2') or
                    course_element.find('a', class_=lambda x: x and 'title' in str(x).lower())
                )
                link_elem = (
                    course_element.find('a', class_=lambda x: x and 'cds-CommonCard-titleLink' in str(x)) or
                    course_element.find('a', href=lambda x: x and '/learn/' in x) or
                    course_element.find('a', href=lambda x: x and '/specializations/' in x) or
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
                elif href.startswith('http'):
                    link = href
            
            img = course_element.find('img')
            thumbnail = img.get('src', '') if img else ''
            if thumbnail:
                thumbnail = self._clean_thumbnail_url(thumbnail)
            
            instructor_elem = (
                course_element.find('p', class_='cds-ProductCard-partnerNames') or
                course_element.find('div', class_=lambda x: x and 'cds-ProductCard-partners' in str(x)) or
                course_element.find('span', class_=lambda x: x and 'instructor' in str(x).lower())
            )
            instructor = self._extract_text_safely(instructor_elem)
            
            return self._standardize_course_data(
                title=title,
                link=link,
                thumbnail=thumbnail,
                instructor=instructor,
                price="",
                rating=""
            )
            
        except Exception:
            return None
    
    def _clean_thumbnail_url(self, url: str) -> str:
        """Remove blur and other unwanted parameters from thumbnail URLs"""
        if not url:
            return url
            
        from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
        
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            # Remove unwanted parameters
            unwanted_params = ['blur', 'px']
            for param in unwanted_params:
                query_params.pop(param, None)
            
            # Reconstruct the URL without unwanted parameters
            new_query = urlencode(query_params, doseq=True)
            cleaned_url = urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                new_query,
                parsed_url.fragment
            ))
            
            return cleaned_url
        except Exception:
            return url