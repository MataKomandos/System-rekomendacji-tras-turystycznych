from src.interface.interfejs_uzytkownika import InterfejsUzytkownika
from src.data_handlers.menadzer_danych_tras import MenadzerDanychTras
from src.analyzers.analiza_pogody import AnalizatorPogodowy
import sys
import os

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stdin.reconfigure(encoding='utf-8')

def pobierz_parametry_wyszukiwania():
    print("\nWitaj w systemie rekomendacji tras turystycznych!")
    print("Wprowadź swoje preferencje:")
    
    while True:
        try:
            min_temp = float(input("\nMinimalna akceptowalna temperatura (°C): "))
            max_temp = float(input("Maksymalna akceptowalna temperatura (°C): "))
            if min_temp > max_temp:
                print("Błąd: Minimalna temperatura nie może być większa niż maksymalna!")
                continue

            min_length = float(input("\nMinimalna długość trasy (km): "))
            max_length = float(input("Maksymalna długość trasy (km): "))
            if min_length > max_length:
                print("Błąd: Minimalna długość nie może być większa niż maksymalna!")
                continue
                
            min_difficulty = float(input("\nMinimalna trudność trasy (1-5): "))
            max_difficulty = float(input("Maksymalna trudność trasy (1-5): "))
            if not (1 <= min_difficulty <= 5 and 1 <= max_difficulty <= 5):
                print("Błąd: Trudność musi być w zakresie 1-5!")
                continue
            if min_difficulty > max_difficulty:
                print("Błąd: Minimalna trudność nie może być większa niż maksymalna!")
                continue
                
            print("\nDostępne regiony:")
            print("1. Tatry")
            print("2. Beskidy")
            print("3. Pieniny")
            print("4. Bieszczady")
            print("5. Wszystkie")
            region_choice = input("\nWybierz region (1-5): ")
            
            region_map = {
                "1": "Tatry",
                "2": "Beskidy",
                "3": "Pieniny",
                "4": "Bieszczady",
                "5": "wszystkie"
            }
            
            if region_choice not in region_map:
                print("Błąd: Nieprawidłowy wybór regionu!")
                continue
                
            return {
                'min_temp': min_temp,
                'max_temp': max_temp,
                'min_length': min_length,
                'max_length': max_length,
                'min_difficulty': min_difficulty,
                'max_difficulty': max_difficulty,
                'region': region_map[region_choice]
            }
        except ValueError:
            print("Błąd: Wprowadź poprawne wartości liczbowe!")
            continue

if __name__ == '__main__':
    menadzer_tras = MenadzerDanychTras()
    analizator_pogodowy = AnalizatorPogodowy()
    
    projekt_dir = os.path.dirname(os.path.abspath(__file__))
    sciezka_trasy = os.path.join(projekt_dir, 'data', 'trasy', 'trasy.csv')
    sciezka_pogoda = os.path.join(projekt_dir, 'data', 'pogoda', 'pogoda.csv')
    
    if not os.path.exists(sciezka_trasy):
        print(f'Błąd: Brak pliku z trasami: {sciezka_trasy}')
        sys.exit(1)
        
    if not os.path.exists(sciezka_pogoda):
        print(f'Błąd: Brak pliku z danymi pogodowymi: {sciezka_pogoda}')
        sys.exit(1)
        
    menadzer_tras.wczytaj_trasy(sciezka_trasy)
    analizator_pogodowy.wczytaj_dane(sciezka_pogoda)
    
    interfejs = InterfejsUzytkownika(menadzer_tras, analizator_pogodowy)
    parametry = pobierz_parametry_wyszukiwania()
    interfejs.wyszukaj_trasy(parametry)