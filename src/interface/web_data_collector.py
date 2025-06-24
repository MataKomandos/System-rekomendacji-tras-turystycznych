import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
import hashlib
from pathlib import Path
import logging

class WebDataCollector:
    def __init__(self, cache_dir: str = 'data/cache'):
        self.cache_dir = cache_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Utworzenie katalogu cache jeśli nie istnieje
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        
        # Konfiguracja loggera
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(cache_dir, 'web_collector.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('WebDataCollector')

    def fetch_route_data(self, url: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Pobierz dane o trasie z podanego URL, używając cache'a jeśli to możliwe."""
        cache_key = self._generate_cache_key(url)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        # Sprawdź czy dane są w cache'u i czy są aktualne
        if not force_refresh and os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    
                # Sprawdź czy cache nie jest starszy niż 7 dni
                cache_date = datetime.fromisoformat(cached_data['cache_timestamp'])
                if datetime.now() - cache_date < timedelta(days=7):
                    self.logger.info(f"Using cached data for {url}")
                    return cached_data['data']
            except Exception as e:
                self.logger.warning(f"Error reading cache for {url}: {str(e)}")
        
        # Pobierz świeże dane
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = self._parse_route_page(response.text)
            
            # Zapisz do cache'a
            cache_data = {
                'cache_timestamp': datetime.now().isoformat(),
                'url': url,
                'data': data
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Successfully fetched and cached data for {url}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching data from {url}: {str(e)}")
            raise

    def fetch_weather_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        """Pobierz prognozę pogody dla podanych współrzędnych."""
        # Użyj OpenWeatherMap API (wymagany klucz API)
        api_key = os.getenv('OPENWEATHER_API_KEY')
        if not api_key:
            self.logger.warning("No OpenWeather API key found in environment variables")
            return {}
            
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=pl"
        cache_key = self._generate_cache_key(f"weather_{lat}_{lon}")
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        # Sprawdź cache (ważny tylko 3 godziny dla prognozy)
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                cache_date = datetime.fromisoformat(cached_data['cache_timestamp'])
                if datetime.now() - cache_date < timedelta(hours=3):
                    return cached_data['data']
            except Exception as e:
                self.logger.warning(f"Error reading weather cache: {str(e)}")
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Zapisz do cache'a
            cache_data = {
                'cache_timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching weather data: {str(e)}")
            return {}

    def fetch_trail_conditions(self, trail_id: str) -> Dict[str, Any]:
        """Pobierz informacje o aktualnych warunkach na szlaku."""
        # Ta metoda mogłaby pobierać dane z różnych źródeł (np. GOPR, parki narodowe)
        # Tutaj przykładowa implementacja
        cache_key = self._generate_cache_key(f"conditions_{trail_id}")
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        # Sprawdź cache (ważny 12 godzin dla warunków)
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                cache_date = datetime.fromisoformat(cached_data['cache_timestamp'])
                if datetime.now() - cache_date < timedelta(hours=12):
                    return cached_data['data']
            except Exception as e:
                self.logger.warning(f"Error reading trail conditions cache: {str(e)}")
        
        # Implementacja pobierania danych z API parków narodowych/GOPR
        # (wymagałoby to dostępu do odpowiednich API)
        return {}

    def clear_cache(self, older_than_days: Optional[int] = None):
        """Wyczyść cache starszy niż podana liczba dni."""
        try:
            for cache_file in os.listdir(self.cache_dir):
                if not cache_file.endswith('.json'):
                    continue
                    
                file_path = os.path.join(self.cache_dir, cache_file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)
                    cache_date = datetime.fromisoformat(cached_data['cache_timestamp'])
                    
                    if older_than_days is None or \
                       datetime.now() - cache_date > timedelta(days=older_than_days):
                        os.remove(file_path)
                        self.logger.info(f"Removed old cache file: {cache_file}")
                except Exception as e:
                    self.logger.warning(f"Error processing cache file {cache_file}: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Error clearing cache: {str(e)}")

    def _generate_cache_key(self, url: str) -> str:
        """Generuj unikalny klucz cache'a dla URL."""
        return hashlib.md5(url.encode()).hexdigest()

    def _parse_route_page(self, html_content: str) -> Dict[str, Any]:
        """Parsuj stronę z opisem trasy i zwróć ustrukturyzowane dane."""
        soup = BeautifulSoup(html_content, 'html.parser')
        data = {
            'title': '',
            'description': '',
            'parameters': {},
            'points_of_interest': [],
            'images': [],
            'warnings': []
        }
        
        # Próba znalezienia tytułu
        title_tag = soup.find(['h1', 'h2'])
        if title_tag:
            data['title'] = title_tag.get_text().strip()
        
        # Próba znalezienia opisu
        description_tags = soup.find_all(['p', 'div'], class_=['description', 'content', 'article-content'])
        if description_tags:
            data['description'] = '\n'.join(tag.get_text().strip() for tag in description_tags)
        
        # Próba znalezienia parametrów trasy
        params_table = soup.find('table', class_=['parameters', 'info', 'details'])
        if params_table:
            rows = params_table.find_all('tr')
            for row in rows:
                cells = row.find_all(['th', 'td'])
                if len(cells) >= 2:
                    key = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()
                    data['parameters'][key] = value
        
        # Próba znalezienia punktów POI
        poi_list = soup.find(['ul', 'ol'], class_=['poi', 'attractions', 'points'])
        if poi_list:
            items = poi_list.find_all('li')
            data['points_of_interest'] = [item.get_text().strip() for item in items]
        
        # Próba znalezienia obrazów
        images = soup.find_all('img')
        for img in images:
            src = img.get('src', '')
            alt = img.get('alt', '')
            if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                data['images'].append({
                    'url': src,
                    'alt': alt
                })
        
        # Próba znalezienia ostrzeżeń
        warnings = soup.find_all(['div', 'p'], class_=['warning', 'alert', 'danger'])
        if warnings:
            data['warnings'] = [w.get_text().strip() for w in warnings]
        
        return data 