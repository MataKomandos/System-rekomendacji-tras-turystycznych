from src.data_handlers.route_rating_manager import RouteRatingManager

def test_reviews():
    manager = RouteRatingManager()
    
    reviews = manager.get_route_reviews(1)
    print("\nRecenzje dla trasy 1:")
    for review in reviews:
        print(f"\nAutor: {review['author']}")
        print(f"Data: {review['date']}")
        print(f"Ocena: {'★' * review['rating']}")
        print(f"Tekst: {review['text']}")
    
    rating = manager.get_route_rating(1)
    print(f"\nŚrednia ocena trasy 1: {rating:.1f}/5.0")
    
    expected_rating = 4.5
    if abs(rating - expected_rating) < 0.01:
        print("✓ Średnia ocena jest poprawna!")
    else:
        print(f"✗ Błąd w obliczaniu średniej! Oczekiwano: {expected_rating}, otrzymano: {rating}")

if __name__ == "__main__":
    test_reviews() 