from src.data_handlers.menadzer_danych_tras import MenadzerDanychTras
from src.data_handlers.menadzer_pogody import MenadzerDanychPogodowych
from src.models.preferencje import PreferencjeUzytkownika
from src.recommenders.rekomendator_tras import RekomendatorTras
import json
import os

class InterfejsUzytkownika:
    def __init__(self):
        self._menadzer_tras = MenadzerDanychTras()
        self._menadzer_pogody = MenadzerDanychPogodowych()
        self._predkosci_terenowe = {
            'mountain': 3.5,
            'lakeside': 5.0,
            'forest': 4.0,
            'plain': 5.5,
            'trail': 4.5,
        }
        
        # Znajdź ścieżkę do katalogu projektu
        self.projekt_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Upewnij się, że katalogi istnieją
        os.makedirs(os.path.join(self.projekt_dir, 'data', 'trasy'), exist_ok=True)
        os.makedirs(os.path.join(self.projekt_dir, 'data', 'pogoda'), exist_ok=True)

    def uruchom(self):
        # Sprawdź czy istnieją wymagane pliki
        sciezka_trasy = os.path.join(self.projekt_dir, 'data', 'trasy', 'trasy.csv')
        sciezka_pogoda = os.path.join(self.projekt_dir, 'data', 'pogoda', 'pogoda.csv')
        
        if not os.path.exists(sciezka_trasy):
            print(f'Błąd: Brak pliku z trasami: {sciezka_trasy}')
            return
            
        if not os.path.exists(sciezka_pogoda):
            print(f'Błąd: Brak pliku z danymi pogodowymi: {sciezka_pogoda}')
            return
        
        data = input('Podaj datę wyprawy z zakresu od 2023-07-01 do 2023-07-07: ')
        from datetime import datetime, date
        try:
            data_obj = datetime.strptime(data, '%Y-%m-%d').date()
        except ValueError:
            print('Błąd: niepoprawny format daty, użyj RRRR-MM-DD')
            return
        if data_obj < date(2023, 7, 1) or data_obj > date(2023, 7, 7):
            print('Błąd: data musi być z zakresu 2023-07-01 do 2023-07-07')
            return
        # pobierz preferencje
        temp_min = float(input('Preferowana minimalna temperatura [°C]: '))
        temp_max = float(input('Preferowana maksymalna temperatura [°C]: '))
        max_opady = float(input('Maksymalne opady [mm]: '))
        max_trud = int(input('Maksymalna trudność (1-5): '))
        max_dl = float(input('Maksymalna długość trasy [km]: '))
        waga_pog = float(input('Waga pogody (0-1): '))
        waga_tr = 1 - waga_pog
        pref = PreferencjeUzytkownika(
            temp_pref=(temp_min, temp_max),
            max_opady_mm=max_opady,
            max_trudnosc=max_trud,
            max_dlugosc_km=max_dl,
            wagi={'pogoda': waga_pog, 'trudnosc': waga_tr}
        )
        # wczytanie danych
        trasy = self._menadzer_tras.wczytaj_trasy(sciezka_trasy)
        pogoda = self._menadzer_pogody.wczytaj_dane(sciezka_pogoda)
        rekom = RekomendatorTras(trasy, pogoda, pref).generuj_rekomendacje(data)
        # wyniki
        print(f"\nRekomendowane trasy na dzień {data}:\n")
        for idx, e in enumerate(rekom, start=1):
            t = e['trasa']
            d = e['dane_pogodowe']
            czas = t.szacuj_czas_przejscia(self._predkosci_terenowe)
            godz = int(czas)
            minuty = int((czas - godz) * 60)
            indeks = d.oblicz_indeks_komfortu()
            kat = ", ".join(t.kategoryzuj()) or 'Brak'
            print(f"{idx}. {t.nazwa} ({t._region})")
            print(f"   Długość: {t.dlugosc_km} km")
            print(f"   Trudność: {t.trudnosc}/5")
            print(f"   Szacowany czas: {godz}h {minuty}min")
            print(f"   Komfort pogodowy: {indeks:.0f}/100")
            print(f"   Kategorie: {kat}\n")
        # zapis do pliku
        zapisz = input('Czy zapisać wyniki do JSON? (t/n): ')
        if zapisz.strip().lower() in ('t', 'tak'):
            out = [
                {
                    'id': e['trasa'].id,
                    'nazwa': e['trasa'].nazwa,
                    'region': e['trasa']._region,
                    'czas_h': round(e['trasa'].szacuj_czas_przejscia(self._predkosci_terenowe), 2),
                    'komfort': round(e['dane_pogodowe'].oblicz_indeks_komfortu(), 1),
                    'kategorie': e['trasa'].kategoryzuj()
                }
                for e in rekom
            ]
            with open('rekomendacje.json', 'w', encoding='utf-8') as f:
                json.dump(out, f, ensure_ascii=False, indent=2)
            print('Zapisano do rekomendacje.json')