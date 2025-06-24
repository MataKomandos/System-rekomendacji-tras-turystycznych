from datetime import datetime
from src.models.preferencje import PreferencjeUzytkownika
from src.models.trasy import Trasa
from src.models.dane_pogodowe import DanePogodowe

class RekomendatorTras:
    def __init__(
        self,
        trasy: list[Trasa],
        pogoda: list[DanePogodowe],
        pref: PreferencjeUzytkownika,
    ):
        self._trasy = trasy
        self._pogoda = pogoda
        self._pref = pref

    def generuj_rekomendacje(self, data: str) -> list[dict]:
        target_date = datetime.strptime(data, '%Y-%m-%d').date()
        wyniki = []
        for trasa in self._trasy:
            # dopasowanie trasowe
            if not trasa.dopasowana_do_preferencji(self._pref):
                continue
            # znajdź dane pogodowe
            dane = next((d for d in self._pogoda if d.lokalizacja == trasa._region and d.data == target_date), None)
            if not dane:
                continue
            pogoda_score = self._pref.zgodnosc_z_pogoda(dane)
            if pogoda_score == 0:
                continue
            trasa_score = self._pref.zgodnosc_z_trasa(trasa)
            # łączny wynik
            w_pogoda = self._pref.wagi.get('pogoda', 0.5)
            w_trasa = self._pref.wagi.get('trudnosc', 0.5)
            score = pogoda_score * w_pogoda + trasa_score * w_trasa
            wyniki.append({
                'trasa': trasa,
                'dane_pogodowe': dane,
                'score': score
            })
        wyniki.sort(key=lambda x: x['score'], reverse=True)
        return wyniki