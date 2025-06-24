from collections import defaultdict
from calendar import month_name
from src.models.dane_pogodowe import DanePogodowe
from typing import Dict, List, Any, Optional
from statistics import mean
from datetime import datetime
import csv
from datetime import datetime, date

import csv
from datetime import datetime
from typing import Optional
from src.models.dane_pogodowe import DanePogodowe

class AnalizatorPogodowy:
    def __init__(self, dane_pogodowe: List[DanePogodowe] = None):
        """Inicjalizuje analizator pogodowy."""
        self._dane = dane_pogodowe or []
        # Mapowanie nazw regionów
        self._region_map = {
            'Tatry': 'Tatry',
            'Beskidy': 'Beskidy',
            'Pieniny': 'Pieniny',
            'Bieszczady': 'Bieszczady',
            'Gorce': 'Tatry',  # Używamy danych z Tatr dla Gorców (najbliższy region)
            'Karkonosze': 'Karkonosze',
            'Jura Krakowsko-Częstochowska': 'Jura Krakowsko-Częstochowska',
            'Góry Stołowe': 'Góry Stołowe',
            'Sudety': 'Sudety',
            'Podkarpacie': 'Podkarpacie',
            'wszystkie': None  # Dla wszystkich regionów
        }

    def pobierz_dane_dla_lokacji(self, lokalizacja: str) -> Optional[DanePogodowe]:
        """
        Pobiera najnowsze dane pogodowe dla danej lokalizacji.
        
        Args:
            lokalizacja: Nazwa lokalizacji
            
        Returns:
            Optional[DanePogodowe]: Dane pogodowe dla lokalizacji lub None jeśli nie znaleziono
        """
        dane_lokalizacji = [d for d in self._dane if d.lokalizacja == lokalizacja]
        if not dane_lokalizacji:
            return None
        # Zwróć najnowsze dane
        return max(dane_lokalizacji, key=lambda x: x.data)

    def wczytaj_dane(self, sciezka: str) -> None:
        """
        Wczytuje dane pogodowe z pliku CSV.
        
        Args:
            sciezka: Ścieżka do pliku CSV z danymi pogodowymi
        """
        try:
            with open(sciezka, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    dane = DanePogodowe(
                        data=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                        lokalizacja=row['location_id'],
                        temp_srednia=float(row['avg_temp']),
                        temp_min=float(row['min_temp']),
                        temp_max=float(row['max_temp']),
                        opady_mm=float(row['precipitation']),
                        godziny_sloneczne=float(row['sunshine_hours']),
                        zachmurzenie_pct=float(row['cloud_cover'])
                    )
                    self._dane.append(dane)
        except Exception as e:
            print(f"Wystąpił błąd podczas wczytywania danych pogodowych: {str(e)}")
            raise

    def statystyki_dla_lokacji(self, region: str, data: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Analizuje dane pogodowe dla danej lokalizacji.
        
        Args:
            region: Nazwa regionu
            data: Data dla której mają być pobrane dane (opcjonalna)
            
        Returns:
            Słownik ze statystykami pogodowymi
        """
        try:
            # Sprawdź czy region jest w mapowaniu
            if region not in self._region_map:
                raise ValueError(f"Nieznany region: {region}")
            
            mapped_region = self._region_map[region]
            
            # Jeśli wybrano wszystkie regiony, użyj pierwszego dostępnego
            if mapped_region is None and self._dane:
                mapped_region = self._dane[0].lokalizacja
            
            # Jeśli nie podano daty, użyj najnowszej dostępnej
            if data is None and self._dane:
                matching_data = [d for d in self._dane if d.lokalizacja == mapped_region]
                if not matching_data:
                    raise ValueError(f"Brak danych pogodowych dla regionu {region}")
                data = max(d.data for d in matching_data)
            
            # Znajdź dane pogodowe dla regionu i daty
            dane = next((d for d in self._dane 
                        if d.lokalizacja == mapped_region 
                        and (data is None or d.data == (data.date() if isinstance(data, datetime) else data))), None)
            
            if not dane:
                raise ValueError(f"Brak danych pogodowych dla regionu {region} na dzień {data}")
            
            # Przygotuj dane w jednolitym formacie
            dane_pogodowe = {
                'avg_temp': dane.temp_srednia,
                'min_temp': dane.temp_min,
                'max_temp': dane.temp_max,
                'precipitation': dane.opady_mm,
                'cloud_cover': dane.zachmurzenie_pct,
                'sunshine_hours': dane.godziny_sloneczne,
                'comfort_index': dane.oblicz_indeks_komfortu()
            }
            
            return dane_pogodowe
            
        except Exception as e:
            print(f"Wystąpił błąd podczas analizy danych pogodowych: {str(e)}")
            raise

    def najlepsze_okresy(self, lok: str, top_n: int = 3) -> List[str]:
        """Zwraca najlepsze miesiące do odwiedzenia danej lokalizacji."""
        # Sprawdź czy region jest w mapowaniu
        if lok not in self._region_map:
            raise ValueError(f"Nieznany region: {lok}")
            
        mapped_region = self._region_map[lok]
        if mapped_region is None and self._dane:
            mapped_region = self._dane[0].lokalizacja
            
        miesiace = defaultdict(list)
        for d in self._dane:
            if d.lokalizacja == mapped_region:
                miesiace[d.data.month].append(d.oblicz_indeks_komfortu())
                
        srednie = []
        for m, vals in miesiace.items():
            srednie.append((m, sum(vals)/len(vals)))
        srednie.sort(key=lambda x: x[1], reverse=True)
        
        return [month_name[m] for m, _ in srednie[:top_n]]