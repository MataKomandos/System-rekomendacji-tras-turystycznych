import re
from datetime import timedelta
from typing import List, Tuple, Optional, Dict

class TextProcessor:
    def __init__(self):
        # Wzorce czasów przejścia
        self.time_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:h|godz|hours?)|(\d+)\s*(?:min|minut)',  # np. 3h, 45min
            r'(\d+)\s*(?:h|godzin(?:y|a)?)\s*(?:i)?\s*(\d+)?\s*(?:min(?:ut)?)?',  # np. 2h 30min
            r'(\d+[.,]\d+)\s*(?:h|godzin(?:y|a)?)'  # np. 2.5 godziny
        ]
        
        # Wzorzec wysokości
        self.elevation_pattern = r'(\d{3,4})\s*m\s*n\.p\.m\.'
        
        # Wzorzec współrzędnych GPS
        self.coords_pattern = r'([NS]?\d{1,2}[°º]\d{1,2}[\'′]\d{1,2}[\"″]?)\s*,?\s*([EW]?\d{1,3}[°º]\d{1,2}[\'′]\d{1,2}[\"″]?)'
        
        # Wzorce ocen
        self.rating_patterns = [
            r'(\d(?:\.\d)?)/5',  # np. 4.5/5
            r'(\d{1,2})/10',     # np. 8/10
            r'★{1,5}'            # np. ★★★★
        ]
        
        # Wzorzec dat
        self.date_pattern = r'(\d{1,2})[-./](\d{1,2})[-./](\d{2,4})'
        
        # Pozostałe wzorce
        self.poi_patterns = {
            'schronisko': r'schronisk[oaui]\s+(?:górskie\s+)?["\']?([A-Za-zżźćńółęąśŻŹĆĄŚĘŁÓŃ\s-]+)["\']?',
            'szczyt': r'szczyt["\']?\s*([A-Za-zżźćńółęąśŻŹĆĄŚĘŁÓŃ\s-]+)["\']?',
            'przełęcz': r'przełęcz["\']?\s*([A-Za-zżźćńółęąśŻŹĆĄŚĘŁÓŃ\s-]+)["\']?'
        }
        
        self.warning_patterns = [
            r'(?:uwaga|ostrzeżenie|niebezpieczeństwo)[!:]?\s*([^.!?\n]+)[.!?\n]',
            r'(?:trudny|niebezpieczny|śliski|stromy)\s+(?:odcinek|fragment|teren)\s*[^.!?\n]*[.!?\n]'
        ]

    def extract_duration(self, text: str) -> Optional[timedelta]:
        """Ekstrahuje czas przejścia z tekstu w różnych formatach."""
        for pattern in self.time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:  # Format: 2h 30min
                    hours = int(match.group(1)) if match.group(1) else 0
                    minutes = int(match.group(2)) if match.group(2) else 0
                    return timedelta(hours=hours, minutes=minutes)
                elif '.' in str(match.group(1)) or ',' in str(match.group(1)):  # Format: 2.5h
                    hours = float(match.group(1).replace(',', '.'))
                    return timedelta(hours=hours)
                else:  # Format: 150min
                    minutes = int(match.group(1))
                    return timedelta(minutes=minutes)
        return None

    def extract_elevation(self, text: str) -> Optional[int]:
        """Ekstrahuje wysokość n.p.m. z tekstu."""
        match = re.search(self.elevation_pattern, text)
        if match:
            return int(match.group(1))
        return None

    def extract_coordinates(self, text: str) -> List[Tuple[str, str]]:
        """Ekstrahuje współrzędne geograficzne z tekstu."""
        return re.findall(self.coords_pattern, text)

    def extract_rating(self, text: str) -> Optional[float]:
        """Ekstrahuje ocenę z tekstu."""
        for pattern in self.rating_patterns:
            match = re.search(pattern, text)
            if match:
                if pattern == r'★{1,5}':
                    # Liczba gwiazdek
                    return len(match.group(0))
                elif '/10' in pattern:
                    # Konwersja oceny z /10 na /5
                    return float(match.group(1)) / 2
                else:
                    # Ocena w skali /5
                    return float(match.group(1))
        return None

    def extract_date(self, text: str) -> Optional[Tuple[int, int, int]]:
        """Ekstrahuje datę z tekstu."""
        match = re.search(self.date_pattern, text)
        if match:
            day, month, year = map(int, match.groups())
            if year < 100:
                year += 2000
            return (day, month, year)
        return None

    def extract_points_of_interest(self, text: str) -> Dict[str, List[str]]:
        """Ekstrahuje punkty charakterystyczne z tekstu."""
        pois = {category: [] for category in self.poi_patterns.keys()}
        
        for category, pattern in self.poi_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                poi_name = match.group(1).strip()
                if poi_name and poi_name not in pois[category]:
                    pois[category].append(poi_name)
                    
        return pois

    def extract_warnings(self, text: str) -> List[str]:
        """Ekstrahuje ostrzeżenia i zagrożenia z opisu trasy."""
        warnings = []
        for pattern in self.warning_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                warning = match.group(0).strip()
                if warning not in warnings:
                    warnings.append(warning)
        return warnings 