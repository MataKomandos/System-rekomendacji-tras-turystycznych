from bs4 import BeautifulSoup
import os
from typing import Dict, Any, Optional, List
from statistics import mean

class RouteRatingManager:
    def __init__(self, reviews_dir: str = 'data/route_reviews'):
        """
        Inicjalizuje menedżera ocen tras.
        
        Args:
            reviews_dir: Ścieżka do katalogu z plikami HTML zawierającymi recenzje
        """
        self.reviews_dir = reviews_dir

    def get_route_rating(self, route_id: int) -> Optional[float]:
        """
        Pobiera średnią ocenę trasy z pliku HTML.
        
        Args:
            route_id: ID trasy
            
        Returns:
            float: Średnia ocena trasy lub None jeśli nie znaleziono ocen
        """
        html_file = os.path.join(self.reviews_dir, f"route_{route_id}.html")
        if not os.path.exists(html_file):
            return None
            
        with open(html_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            
        # Znajdź wszystkie oceny (gwiazdki)
        ratings = []
        for rating_span in soup.find_all('span', class_='rating'):
            stars = rating_span.text.count('★')
            if stars > 0:
                ratings.append(stars)
                
        return mean(ratings) if ratings else None

    def get_route_reviews(self, route_id: int) -> List[Dict[str, Any]]:
        """
        Pobiera wszystkie recenzje trasy z pliku HTML.
        
        Args:
            route_id: ID trasy
            
        Returns:
            List[Dict[str, Any]]: Lista recenzji z danymi (autor, data, tekst, ocena)
        """
        html_file = os.path.join(self.reviews_dir, f"route_{route_id}.html")
        if not os.path.exists(html_file):
            return []
            
        with open(html_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            
        reviews = []
        for review_div in soup.find_all('div', class_='review-entry'):
            # Pobierz ocenę
            rating_span = review_div.find('span', class_='rating')
            rating = rating_span.text.count('★') if rating_span else 0
            
            # Pobierz autora i datę
            author_date = review_div.find('p', recursive=False)
            if author_date:
                author_text = author_date.find('strong').text if author_date.find('strong') else ''
                date_text = author_date.text.split('(')[-1].strip('):') if '(' in author_date.text else ''
            else:
                author_text = ''
                date_text = ''
            
            # Pobierz treść recenzji
            review_text = review_div.find_all('p')[-1].text if len(review_div.find_all('p')) > 1 else ''
            
            reviews.append({
                'author': author_text,
                'date': date_text,
                'text': review_text,
                'rating': rating
            })
            
        return reviews

    def get_route_info(self, route_id: int) -> Optional[Dict[str, Any]]:
        """
        Pobiera podstawowe informacje o trasie z pliku HTML.
        
        Args:
            route_id: ID trasy
            
        Returns:
            Dict[str, Any]: Słownik z informacjami o trasie lub None jeśli nie znaleziono pliku
        """
        html_file = os.path.join(self.reviews_dir, f"route_{route_id}.html")
        if not os.path.exists(html_file):
            return None
            
        with open(html_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            
        info = {}
        
        # Pobierz nazwę trasy
        title = soup.find('h2')
        if title:
            info['nazwa'] = title.text.strip()
            
        # Pobierz parametry trasy
        params_table = soup.find('table', class_='route-params')
        if params_table:
            for row in params_table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) == 2:
                    key = cells[0].text.strip().rstrip(':')
                    value = cells[1].text.strip()
                    info[key.lower()] = value
                    
        return info 