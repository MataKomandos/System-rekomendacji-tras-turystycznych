from typing import List, Optional, Dict, Any
from datetime import timedelta
import re
from src.data_handlers.route_rating_manager import RouteRatingManager

class Trasa:
    def __init__(
        self,
        id: int,
        nazwa: str,
        region: str,
        dlugosc_km: float,
        czas_przejscia: str,
        trudnosc: float,
        przewyzszenie_m: float,
        punkt_startowy: str,
        punkt_koncowy: str,
        opis: str,
        kategoria: str
    ):
        self._id = id
        self._nazwa = nazwa
        self._region = region
        self._dlugosc_km = dlugosc_km
        self._czas_przejscia = self._parsuj_czas(czas_przejscia)
        self._trudnosc = trudnosc
        self._przewyzszenie_m = przewyzszenie_m
        self._punkt_startowy = punkt_startowy
        self._punkt_koncowy = punkt_koncowy
        self._opis = opis
        self._kategoria = kategoria
        self._rating_manager = RouteRatingManager()

    def _parsuj_czas(self, czas_str: str) -> Optional[timedelta]:
        """Parsuje string z czasem przejścia na obiekt timedelta."""
        if not czas_str:
            return None
            
        # Wzorzec dla formatu "Xh Ymin" lub "X.Yh"
        pattern = r'(\d+)(?:\s*h\s*(?:(\d+)\s*min)?|\.\d+h)'
        match = re.match(pattern, czas_str)
        
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2)) if match.group(2) else 0
            return timedelta(hours=hours, minutes=minutes)
        return None

    @property
    def id(self) -> int:
        return self._id

    @property
    def nazwa(self) -> str:
        return self._nazwa

    @property
    def region(self) -> str:
        return self._region

    @property
    def dlugosc_km(self) -> float:
        return self._dlugosc_km

    @property
    def czas_przejscia(self) -> Optional[timedelta]:
        return self._czas_przejscia

    @property
    def trudnosc(self) -> float:
        return self._trudnosc

    @property
    def przewyzszenie_m(self) -> float:
        return self._przewyzszenie_m

    @property
    def punkt_startowy(self) -> str:
        return self._punkt_startowy

    @property
    def punkt_koncowy(self) -> str:
        return self._punkt_koncowy

    @property
    def opis(self) -> str:
        return self._opis

    @property
    def kategoria(self) -> str:
        return self._kategoria

    @property
    def ocena(self) -> Optional[float]:
        """Pobiera średnią ocenę trasy z pliku HTML."""
        return self._rating_manager.get_route_rating(self._id)

    def get_reviews(self) -> List[Dict[str, Any]]:
        """Pobiera wszystkie recenzje trasy."""
        return self._rating_manager.get_route_reviews(self._id)

    def szacuj_czas_przejscia(self, predkosci_terenowe: dict) -> float:
        if self._czas_przejscia:
            return self._czas_przejscia.total_seconds() / 3600  # Konwersja na godziny
            
        # Jeśli brak zdefiniowanego czasu, oblicz szacunkowo
        predkosc = predkosci_terenowe.get(self._kategoria, 4.0)  # km/h domyślnie 4 km/h
        czas_podstawowy = self._dlugosc_km / predkosc
        # Dodatek czasu za przewyższenie: +1h na każde 600m w górę
        czas_wzwyzszenie = (self._przewyzszenie_m / 600.0)
        # Mnożnik za trudność: od 1.0 (łatwe) do 1.8 (bardzo trudne)
        multiplier = 1.0 + (self._trudnosc - 1) * 0.2
        return (czas_podstawowy + czas_wzwyzszenie) * multiplier

    def kategoryzuj(self) -> List[str]:
        kategorie = [self._kategoria]  # Dodaj podstawową kategorię
        
        # Rodzinne: trudność <=2 i długość <=10km
        if self._trudnosc <= 2 and self._dlugosc_km <= 10:
            kategorie.append("Rodzinne")
            
        # Widokowe: jeśli w opisie są odpowiednie słowa kluczowe
        if any(slowo in self._opis.lower() for slowo in ["widok", "panoram", "jezior"]):
            kategorie.append("Widokowe")
            
        # Sportowe: trudność >=3 lub długość >=20km
        if self._trudnosc >= 3 or self._dlugosc_km >= 20:
            kategorie.append("Sportowe")
            
        # Ekstremalne: trudność >=4 lub przewyższenie >=1000m
        if self._trudnosc >= 4 or self._przewyzszenie_m >= 1000:
            kategorie.append("Ekstremalne")
            
        return list(set(kategorie))  # Usuń duplikaty

    def dopasowana_do_preferencji(self, pref) -> bool:
        return (
            self._trudnosc <= pref.max_trudnosc and
            self._dlugosc_km <= pref.max_dlugosc_km
        )