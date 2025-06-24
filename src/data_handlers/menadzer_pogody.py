import csv
from datetime import datetime
from src.models.dane_pogodowe import DanePogodowe

class MenadzerDanychPogodowych:
    def wczytaj_dane(self, sciezka: str) -> list[DanePogodowe]:
        dane = []
        with open(sciezka, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                date_obj = datetime.strptime(row['date'], '%Y-%m-%d').date()
                dane.append(DanePogodowe(
                    data=date_obj,
                    lokalizacja=row['location_id'],
                    temp_srednia=float(row['avg_temp']),
                    temp_min=float(row['min_temp']),
                    temp_max=float(row['max_temp']),
                    opady_mm=float(row['precipitation']),
                    godziny_sloneczne=float(row['sunshine_hours']),
                    zachmurzenie_pct=float(row['cloud_cover']),
                ))
        return dane