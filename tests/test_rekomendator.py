from datetime import date

from src.models.dane_pogodowe import DanePogodowe
from src.models.preferencje import PreferencjeUzytkownika
from src.models.trasy import Trasa
from src.recommenders.rekomendator_tras import RekomendatorTras

DZIEN = date(2023, 7, 1)


def pogoda(region="Tatry", temp=20.0, opady=0.0, chmury=0.0):
    return DanePogodowe(DZIEN, region, temp, temp - 5, temp + 5, opady, 8.0, chmury)


def trasa(id, nazwa, region="Tatry", dlugosc=8.0, trudnosc=2.0):
    return Trasa(id, nazwa, region, dlugosc, "3h", trudnosc, 300, "Start", "Meta", "Opis", "Górska")


def preferencje(**kw):
    domyslne = dict(temp_pref=(10, 28), max_opady_mm=5, max_trudnosc=4, max_dlugosc_km=15)
    domyslne.update(kw)
    return PreferencjeUzytkownika(**domyslne)


def test_idealna_pogoda_daje_indeks_komfortu_100():
    assert pogoda(temp=20, opady=0, chmury=0).oblicz_indeks_komfortu() == 100


def test_deszcz_obniza_indeks_komfortu():
    assert pogoda(opady=10).oblicz_indeks_komfortu() < pogoda(opady=0).oblicz_indeks_komfortu()


def test_zbyt_duze_opady_wykluczaja_dzien():
    assert preferencje(max_opady_mm=5).zgodnosc_z_pogoda(pogoda(opady=6)) == 0.0


def test_trasa_poza_limitami_nie_jest_dopasowana():
    pref = preferencje(max_trudnosc=3, max_dlugosc_km=10)
    assert trasa(1, "OK", dlugosc=8, trudnosc=2).dopasowana_do_preferencji(pref)
    assert not trasa(2, "Za trudna", trudnosc=4).dopasowana_do_preferencji(pref)
    assert not trasa(3, "Za dluga", dlugosc=12).dopasowana_do_preferencji(pref)


def test_rekomendator_pomija_trasy_niepasujace_do_preferencji():
    trasy = [trasa(1, "Latwa"), trasa(2, "Zbyt trudna", trudnosc=5)]
    wyniki = RekomendatorTras(trasy, [pogoda()], preferencje()).generuj_rekomendacje("2023-07-01")
    assert [w['trasa'].nazwa for w in wyniki] == ["Latwa"]


def test_rekomendator_sortuje_od_najlepszej():
    trasy = [trasa(1, "Trudna", trudnosc=4, dlugosc=14), trasa(2, "Latwa", trudnosc=1, dlugosc=4)]
    wyniki = RekomendatorTras(trasy, [pogoda()], preferencje()).generuj_rekomendacje("2023-07-01")
    assert [w['trasa'].nazwa for w in wyniki] == ["Latwa", "Trudna"]
    assert wyniki[0]['score'] > wyniki[1]['score']


def test_rekomendator_pomija_region_bez_danych_pogodowych():
    trasy = [trasa(1, "W Tatrach", region="Tatry"), trasa(2, "W Pieninach", region="Pieniny")]
    wyniki = RekomendatorTras(trasy, [pogoda("Tatry")], preferencje()).generuj_rekomendacje("2023-07-01")
    assert [w['trasa'].nazwa for w in wyniki] == ["W Tatrach"]


def test_zla_pogoda_wyklucza_trase():
    wyniki = RekomendatorTras([trasa(1, "Latwa")], [pogoda(opady=20)], preferencje()).generuj_rekomendacje("2023-07-01")
    assert wyniki == []
