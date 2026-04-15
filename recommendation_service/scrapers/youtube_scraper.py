import os
import requests
from typing import List, Dict, Optional
from .base_scraper import BaseScraper

class YouTubeScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            base_url="https://www.googleapis.com/youtube/v3",
            headers={}
        )
        self.api_key = os.environ.get('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY environment variable is required")
    
    def search_courses(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for course playlists on YouTube"""
        search_url = f"{self.base_url}/search"
        params = {
            'part': 'snippet',
            'q': f"{query} course tutorial playlist",
            'type': 'playlist',
            'maxResults': limit,
            'key': self.api_key,
            'order': 'relevance'
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'items' not in data:
                return []
            
            courses = []
            for item in data['items']:
                course_data = self._parse_playlist_item(item)
                if course_data:
                    courses.append(course_data)
            
            return courses
            
        except Exception as e:
            print(f"Error searching YouTube: {str(e)}")
            return []
    
    def _parse_playlist_item(self, item: Dict) -> Optional[Dict]:
        """Parse a YouTube playlist item into course data"""
        try:
            snippet = item.get('snippet', {})
            
            title = snippet.get('title', '')
            if not title:
                return None
            
            playlist_id = item.get('id', {}).get('playlistId', '')
            link = f"https://www.youtube.com/playlist?list={playlist_id}" if playlist_id else ""
            
            # Get the best quality thumbnail
            thumbnails = snippet.get('thumbnails', {})
            thumbnail = ""
            for quality in ['maxres', 'high', 'medium', 'default']:
                if quality in thumbnails:
                    thumbnail = thumbnails[quality].get('url', '')
                    break
            
            channel_title = snippet.get('channelTitle', '')
            description = snippet.get('description', '')
            
            return self._standardize_course_data(
                title=title,
                link=link,
                thumbnail=thumbnail,
                instructor=channel_title,
                price="Free",
                rating=""
            )
            
        except Exception:
            return None
    
    def _parse_course_card(self, course_element):
        """Required by BaseScraper but not used in YouTube scraper"""
        return None
    
    def _make_request(self, url: str, params: Dict = None):
        """Override base class method since we don't use BeautifulSoup for API calls"""
        return None