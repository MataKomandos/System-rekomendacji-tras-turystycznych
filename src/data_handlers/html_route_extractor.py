from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import timedelta

@dataclass
class RouteParameters:
    difficulty: Optional[str] = None
    distance: Optional[float] = None  # in kilometers
    elevation_gain: Optional[int] = None  # in meters
    duration: Optional[timedelta] = None
    start_point: Optional[str] = None
    end_point: Optional[str] = None
    attractions: List[str] = None
    
    def __post_init__(self):
        if self.attractions is None:
            self.attractions = []

class HTMLRouteExtractor:
    def __init__(self):
        self.difficulty_keywords = {
            'łatwa': ['łatwa', 'łatwy', 'prosta', 'prosty', 'dla początkujących'],
            'średnia': ['średnia', 'średni', 'umiarkowana', 'umiarkowany'],
            'trudna': ['trudna', 'trudny', 'wymagająca', 'wymagający', 'dla zaawansowanych']
        }
        
        self.attraction_keywords = [
            'zamek', 'pałac', 'ruiny', 'jezioro', 'wodospad', 'jaskinia',
            'szczyt', 'przełęcz', 'schronisko', 'punkt widokowy', 'panorama'
        ]

    def extract_route_info(self, html_content: str) -> Dict[str, Any]:
        """Ekstrahuje informacje o trasie z dokumentu HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')
        route_data = {
            'title': '',
            'description': '',
            'parameters': {},
            'reviews': [],
            'images': [],
            'map_data': None
        }
        
        # Ekstrakcja tytułu
        title_elem = soup.find('h2')
        if title_elem:
            route_data['title'] = title_elem.text.strip()
        
        # Ekstrakcja parametrów z tabeli
        params_table = soup.find('table', class_='route-params')
        if params_table:
            rows = params_table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].text.strip().rstrip(':')
                    value = cells[1].text.strip()
                    route_data['parameters'][key] = value
        
        # Ekstrakcja opisu
        description_div = soup.find('div', class_='route-description')
        if description_div:
            route_data['description'] = description_div.text.strip()
        
        # Ekstrakcja galerii zdjęć
        gallery_div = soup.find('div', class_='gallery')
        if gallery_div:
            images = gallery_div.find_all('img')
            for img in images:
                src = img.get('src', '')
                alt = img.get('alt', '')
                if src:
                    route_data['images'].append({
                        'url': src,
                        'alt': alt or ''
                    })
        
        # Ekstrakcja danych mapy
        map_div = soup.find('div', id='map')
        if map_div:
            # Próba ekstrakcji współrzędnych z atrybutów data-*
            route_data['map_data'] = {
                'center_lat': map_div.get('data-lat'),
                'center_lon': map_div.get('data-lon'),
                'zoom': map_div.get('data-zoom'),
                'markers': self._extract_map_markers(map_div)
            }
        
        # Ekstrakcja recenzji użytkowników
        reviews_div = soup.find_all('div', class_='user-review')
        for review_div in reviews_div:
            review = self._extract_review(review_div)
            if review:
                route_data['reviews'].append(review)
        
        return route_data

    def _extract_map_markers(self, map_div: BeautifulSoup) -> List[Dict[str, Any]]:
        """Ekstrahuje markery z elementu mapy."""
        markers = []
        marker_elements = map_div.find_all('div', class_='marker')
        
        for marker in marker_elements:
            marker_data = {
                'lat': marker.get('data-lat'),
                'lon': marker.get('data-lon'),
                'title': marker.get('data-title', ''),
                'description': marker.get('data-description', '')
            }
            if marker_data['lat'] and marker_data['lon']:
                markers.append(marker_data)
        
        return markers

    def _extract_review(self, review_div: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Ekstrahuje dane recenzji użytkownika."""
        if not review_div:
            return None
            
        review_data = {
            'rating': None,
            'text': '',
            'date': None,
            'author': None
        }
        
        # Ekstrakcja oceny
        rating_span = review_div.find('span', class_='rating')
        if rating_span:
            stars = rating_span.text.strip()
            review_data['rating'] = len(stars)
        
        # Ekstrakcja tekstu recenzji
        text_elem = review_div.find('p')
        if text_elem:
            review_data['text'] = text_elem.text.strip()
        
        # Ekstrakcja daty (jeśli jest)
        date_elem = review_div.find(class_='review-date')
        if date_elem:
            review_data['date'] = date_elem.text.strip()
        
        # Ekstrakcja autora (jeśli jest)
        author_elem = review_div.find(class_='review-author')
        if author_elem:
            review_data['author'] = author_elem.text.strip()
        
        return review_data if review_data['text'] or review_data['rating'] else None

    def _parse_duration(self, duration_str: str) -> Optional[timedelta]:
        """Parsuje string z czasem przejścia na obiekt timedelta."""
        if not duration_str:
            return None
            
        # Wzorzec dla formatu "X-Y godzin"
        range_match = re.match(r'(\d+)\s*-\s*(\d+)\s*(?:h|godzin)', duration_str)
        if range_match:
            # Bierzemy średnią z zakresu
            min_hours = int(range_match.group(1))
            max_hours = int(range_match.group(2))
            return timedelta(hours=(min_hours + max_hours) / 2)
        
        # Wzorzec dla formatu "X godzin Y minut"
        full_match = re.match(r'(\d+)\s*(?:h|godzin)?\s*(?:i)?\s*(\d+)?\s*(?:min)?', duration_str)
        if full_match:
            hours = int(full_match.group(1)) if full_match.group(1) else 0
            minutes = int(full_match.group(2)) if full_match.group(2) else 0
            return timedelta(hours=hours, minutes=minutes)
        
        return None

    def _parse_distance(self, distance_str: str) -> Optional[float]:
        """Parsuje string z dystansem na liczbę kilometrów."""
        if not distance_str:
            return None
            
        match = re.search(r'(\d+(?:[.,]\d+)?)\s*km', distance_str)
        if match:
            return float(match.group(1).replace(',', '.'))
        return None

    def _parse_elevation(self, elevation_str: str) -> Optional[int]:
        """Parsuje string z przewyższeniem na liczbę metrów."""
        if not elevation_str:
            return None
            
        match = re.search(r'(\d+)\s*m', elevation_str)
        if match:
            return int(match.group(1))
        return None 