from typing import List, Dict, Any, Optional
import os
from src.models.trasy import Trasa
from src.reports.pdf_report_generator import PDFReportGenerator
from src.analyzers.analiza_pogody import AnalizatorPogodowy
from src.data_handlers.menadzer_danych_tras import MenadzerDanychTras
from src.data_handlers.route_data_generator import RouteDataGenerator
from src.reports.chart_generator import ChartGenerator

class InterfejsUzytkownika:
    def __init__(self, menadzer_tras: MenadzerDanychTras, analizator_pogodowy: AnalizatorPogodowy):
        self._menadzer_tras = menadzer_tras
        self._analizator_pogodowy = analizator_pogodowy
        
    def generuj_raport(self, trasy: List[Trasa], parametry_wyszukiwania: Dict[str, Any]) -> None:
        """Generuje raport PDF z rekomendacjami tras."""
        try:
            # Przygotuj katalog na raporty
            os.makedirs('raporty', exist_ok=True)
            
            # Konwertuj trasy na format wymagany przez generator raportów
            trasy_dict = []
            for trasa in trasy:
                dane_pogodowe = self._analizator_pogodowy.pobierz_dane_dla_lokacji(trasa.region)
                temp_info = f"{dane_pogodowe.temp_srednia}°C" if dane_pogodowe else "brak danych"
                
                # Oblicz czas w godzinach
                czas_h = 0.0
                if hasattr(trasa, 'czas_przejscia'):
                    try:
                        czas_h = float(trasa.czas_przejscia.split('h')[0])
                    except (ValueError, AttributeError, IndexError):
                        czas_h = trasa.dlugosc_km / 4.0  # Przybliżony czas: 4 km/h
                else:
                    czas_h = trasa.dlugosc_km / 4.0  # Przybliżony czas: 4 km/h
                
                # Generuj dane profilu wysokościowego
                route_data_gen = RouteDataGenerator()
                elevation_data = route_data_gen.generate_elevation_profile({
                    'region': trasa.region,
                    'distance': trasa.dlugosc_km,
                    'czas_h': czas_h
                })
                
                trasy_dict.append({
                    'nazwa': trasa.nazwa,
                    'name': trasa.nazwa,  # dodajemy też klucz 'name' dla kompatybilności
                    'region': trasa.region,
                    'distance': trasa.dlugosc_km,
                    'duration': trasa.czas_przejscia if hasattr(trasa, 'czas_przejscia') else "brak danych",
                    'difficulty': trasa.trudnosc,
                    'elevation_gain': trasa.przewyzszenie_m if hasattr(trasa, 'przewyzszenie_m') else 0,
                    'start_point': trasa.punkt_startowy if hasattr(trasa, 'punkt_startowy') else "brak danych",
                    'end_point': trasa.punkt_koncowy if hasattr(trasa, 'punkt_koncowy') else "brak danych",
                    'description': trasa.opis if hasattr(trasa, 'opis') else "",
                    'category': trasa.kategoria if hasattr(trasa, 'kategoria') else "brak kategorii",
                    'rating': trasa.ocena if hasattr(trasa, 'ocena') else 0,
                    'temperature': temp_info,
                    'czas_h': czas_h,  # Dodajemy czas w godzinach
                    'elevation_data': elevation_data  # Dodajemy dane profilu wysokościowego
                })
            
            # Pobierz dane pogodowe dla regionów
            dane_pogodowe = {}
            for trasa in trasy:
                if trasa.region not in dane_pogodowe:
                    dane_pogodowe[trasa.region] = self._analizator_pogodowy.statystyki_dla_lokacji(trasa.region)
            
            # Utwórz generator raportów
            generator = PDFReportGenerator(output_dir='raporty')
            
            # Wygeneruj raport
            sciezka_raportu = generator.generate_route_report(
                routes_data=trasy_dict,
                search_params=parametry_wyszukiwania,
                weather_data=dane_pogodowe
            )
            
            print(f"\nRaport został wygenerowany i zapisany w: {sciezka_raportu}")
            
        except Exception as e:
            print(f"\nWystąpił błąd podczas generowania raportu: {str(e)}")
            raise 

    def wyszukaj_trasy(self, parametry: Dict[str, Any]) -> List[Trasa]:
        """Wyszukuje trasy na podstawie podanych parametrów."""
        try:
            # Wyszukaj trasy spełniające kryteria
            znalezione_trasy = self._menadzer_tras.wyszukaj_trasy(parametry)
            
            # Filtruj trasy na podstawie temperatury
            if 'min_temp' in parametry and 'max_temp' in parametry:
                aktualne_trasy = []
                for trasa in znalezione_trasy:
                    dane_pogodowe = self._analizator_pogodowy.pobierz_dane_dla_lokacji(trasa.region)
                    if dane_pogodowe:
                        if (parametry['min_temp'] <= dane_pogodowe.temp_srednia <= parametry['max_temp']):
                            aktualne_trasy.append(trasa)
                znalezione_trasy = aktualne_trasy
            
            if not znalezione_trasy:
                print("\nNie znaleziono tras spełniających podane kryteria.")
                return []
            
            print(f"\nZnaleziono {len(znalezione_trasy)} tras spełniających kryteria:")
            for i, trasa in enumerate(znalezione_trasy, 1):
                dane_pogodowe = self._analizator_pogodowy.pobierz_dane_dla_lokacji(trasa.region)
                temp_info = f", Temperatura: {dane_pogodowe.temp_srednia}°C" if dane_pogodowe else ""
                
                print(f"\n{i}. {trasa.nazwa}")
                print(f"   Region: {trasa.region}")
                print(f"   Długość: {trasa.dlugosc_km} km")
                print(f"   Trudność: {trasa.trudnosc}/5")
                print(f"   Przewyższenie: {trasa.przewyzszenie_m} m{temp_info}")
            
            # Generuj raport PDF
            print("\nGeneruję raport PDF z rekomendacjami...")
            self.generuj_raport(znalezione_trasy, parametry)
            
            return znalezione_trasy
            
        except Exception as e:
            print(f"\nWystąpił błąd podczas wyszukiwania tras: {str(e)}")
            raise 