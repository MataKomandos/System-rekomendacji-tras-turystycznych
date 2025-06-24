from typing import Tuple
from src.models.dane_pogodowe import DanePogodowe

class PreferencjeUzytkownika:
    def __init__(
        self,
        temp_pref: Tuple[float, float],
        max_opady_mm: float,
        max_trudnosc: int,
        max_dlugosc_km: float,
        wagi: dict = None,
    ):
        self.temp_pref = temp_pref
        self.max_opady_mm = max_opady_mm
        self.max_trudnosc = max_trudnosc
        self.max_dlugosc_km = max_dlugosc_km
        # wagi: {"pogoda":..., "trudnosc":...}
        self.wagi = wagi or {"pogoda": 0.6, "trudnosc": 0.4}

    def zgodnosc_z_trasa(self, trasa) -> float:
        # Ocena trudności i długości (0-1)
        diff_score = max(0, 1 - (trasa.trudnosc / self.max_trudnosc))
        length_score = max(0, 1 - (trasa.dlugosc_km / self.max_dlugosc_km))
        w = self.wagi.get("trudnosc", 0.5)
        return diff_score * w + length_score * (1 - w)

    def zgodnosc_z_pogoda(self, dane: DanePogodowe) -> float:
        if dane.opady_mm > self.max_opady_mm:
            return 0.0
        return dane.oblicz_indeks_komfortu() / 100.0

    def aktualizuj_preferencje(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)