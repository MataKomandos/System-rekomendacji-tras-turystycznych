from datetime import date

class DanePogodowe:
    def __init__(
        self,
        data: date,
        lokalizacja: str,
        temp_srednia: float,
        temp_min: float,
        temp_max: float,
        opady_mm: float,
        godziny_sloneczne: float,
        zachmurzenie_pct: float,
    ):
        self.data = data
        self.lokalizacja = lokalizacja
        self.temp_srednia = temp_srednia
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.opady_mm = opady_mm
        self.godziny_sloneczne = godziny_sloneczne
        self.zachmurzenie_pct = zachmurzenie_pct

    def czy_sloneczny(self) -> bool:
        return self.godziny_sloneczne > (24 - self.zachmurzenie_pct/100*24)

    def czy_deszczowy(self) -> bool:
        return self.opady_mm > 0

    def oblicz_indeks_komfortu(self) -> float:
        temp_score = max(0, 100 - abs(self.temp_srednia - 20) * 3)
        rain_penalty = min(self.opady_mm * 2, 100)
        rain_score = 100 - rain_penalty
        cloud_score = 100 - self.zachmurzenie_pct
        indeks = temp_score * 0.6 + rain_score * 0.3 + cloud_score * 0.1
        return max(0, min(100, indeks))