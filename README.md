# Rekomendator Tras Turystycznych 🏔️

System rekomendacji tras turystycznych z generowaniem szczegółowych raportów PDF.

## 📋 Spis treści
- [Opis projektu](#opis-projektu)
- [Funkcjonalności](#funkcjonalności)
- [Wymagania systemowe](#wymagania-systemowe)
- [Instalacja](#instalacja)
- [Użytkowanie](#użytkowanie)
- [Struktura projektu](#struktura-projektu)
- [Generowane raporty](#generowane-raporty)
- [Licencja](#licencja)

## 🎯 Opis projektu

Rekomendator Tras Turystycznych to zaawansowany system, który pomaga użytkownikom w wyborze tras turystycznych na podstawie ich preferencji. System analizuje różnorodne dane, w tym warunki pogodowe, trudność tras, opinie użytkowników i generuje szczegółowe raporty w formacie PDF.

## ✨ Funkcjonalności

- **Rekomendacje tras** na podstawie:
  - Preferencji użytkownika
  - Warunków pogodowych
  - Trudności trasy
  - Długości trasy
  - Regionu
  
- **Analiza danych**:
  - Profile wysokościowe tras
  - Analiza porównawcza tras
  - Analiza sezonowości
  - Statystyki i wykresy

- **Generowanie raportów PDF** zawierających:
  - Profile wysokościowe tras
  - Analizę porównawczą
  - Analizę sezonowości
  - Tabelę zbiorczą
  - Dane źródłowe

## 💻 Wymagania systemowe

- Python 3.8 lub nowszy
- System operacyjny: Windows/Linux/MacOS
- Minimum 4GB RAM
- Dostęp do internetu (dla danych pogodowych)

## 🚀 Instalacja

1. Sklonuj repozytorium:
```bash
git clone [adres-repozytorium]
cd mainRekomendator
```

2. Utwórz wirtualne środowisko Python:
```bash
python -m venv venv
```

3. Aktywuj wirtualne środowisko:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/MacOS:
```bash
source venv/bin/activate
```

4. Zainstaluj wymagane pakiety:
```bash
pip install -r requirements.txt
```

## 🎮 Użytkowanie

1. Uruchom program główny:
```bash
python src/main.py
```

2. Wprowadź swoje preferencje:
   - Minimalna/maksymalna temperatura
   - Minimalna/maksymalna długość trasy
   - Poziom trudności
   - Preferowany region

3. System wygeneruje raport PDF z rekomendacjami w katalogu `raporty/`

## 📁 Struktura projektu

```
mainRekomendator/
├── data/                   # Dane wejściowe
│   ├── maps/              # Mapy tras
│   ├── pogoda/            # Dane pogodowe
│   ├── route_reviews/     # Recenzje tras
│   └── trasy/             # Informacje o trasach
├── src/                   # Kod źródłowy
│   ├── analyzers/         # Moduły analizy danych
│   ├── data_handlers/     # Obsługa danych
│   ├── interface/         # Interfejs użytkownika
│   ├── models/            # Modele danych
│   ├── recommenders/      # System rekomendacji
│   └── reports/           # Generowanie raportów
├── raporty/              # Wygenerowane raporty PDF
├── tests/                # Testy
└── requirements.txt      # Zależności projektu
```

## 📊 Generowane raporty

Raporty PDF zawierają:

1. **Profile wysokościowe tras**
   - Wizualizacje profili wysokościowych
   - Dane o przewyższeniach

2. **Analiza porównawcza**
   - Porównanie długości tras
   - Rozkład kategorii
   - Opinie użytkowników

3. **Analiza sezonowości**
   - Mapy ciepła dostępności
   - Dane pogodowe

4. **Tabela zbiorcza**
   - Zestawienie wszystkich tras
   - Kluczowe parametry

5. **Aneks**
   - Źródła danych
   - Metodologia
