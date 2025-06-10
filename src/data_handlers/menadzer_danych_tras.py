import csv
from typing import List, Dict, Any
from src.models.trasy import Trasa
from datetime import datetime

class MenadzerDanychTras:
    def __init__(self):
        self._trasy = []

    def wczytaj_trasy(self, sciezka: str) -> List[Trasa]:
        
        try:
            with open(sciezka, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    trasa = Trasa(
                        id=int(row['id']),
                        nazwa=row['nazwa'],
                        region=row['region'],
                        dlugosc_km=float(row['dlugosc_km']),
                        czas_przejscia=row['czas_przejscia'],
                        trudnosc=float(row['trudnosc']),
                        przewyzszenie_m=int(row['przewyzszenie_m']),
                        punkt_startowy=row['punkt_startowy'],
                        punkt_koncowy=row['punkt_koncowy'],
                        opis=row['opis'],
                        kategoria=row['kategoria']
                    )
                    self._trasy.append(trasa)
            return self._trasy
        except Exception as e:
            print(f"Wystąpił błąd podczas wczytywania tras: {str(e)}")
            raise

    def wyszukaj_trasy(self, parametry: Dict[str, Any]) -> List[Trasa]:
        
        wyniki = []
        
        for trasa in self._trasy:           
            if 'min_length' in parametry and trasa.dlugosc_km < parametry['min_length']:
                continue
            if 'max_length' in parametry and trasa.dlugosc_km > parametry['max_length']:
                continue
                
            if 'min_difficulty' in parametry and trasa.trudnosc < parametry['min_difficulty']:
                continue
            if 'max_difficulty' in parametry and trasa.trudnosc > parametry['max_difficulty']:
                continue
                
            if 'region' in parametry and parametry['region'] != 'wszystkie':
                if trasa.region != parametry['region']:
                    continue
            
            wyniki.append(trasa)
            
        return wyniki