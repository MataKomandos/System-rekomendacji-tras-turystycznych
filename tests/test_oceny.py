from src.data_handlers.route_rating_manager import RouteRatingManager


def test_srednia_ocena_trasy_1():
    manager = RouteRatingManager()
    assert abs(manager.get_route_rating(1) - 4.5) < 0.01


def test_recenzje_maja_autora_ocene_i_tekst():
    manager = RouteRatingManager()
    recenzje = manager.get_route_reviews(1)
    assert recenzje
    for r in recenzje:
        assert 1 <= r['rating'] <= 5
        assert r['author'] and r['text']
