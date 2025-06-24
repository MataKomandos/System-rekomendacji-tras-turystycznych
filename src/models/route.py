from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from src.analyzers.review_analyzer import Review

@dataclass
class Route:
    name: str
    description: str
    difficulty: str
    distance: float  # w kilometrach
    duration: timedelta
    elevation_gain: int  # w metrach
    start_point: str
    end_point: str
    category: str
    coordinates: List[tuple]  # lista punktów (lat, lon)
    points_of_interest: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    reviews: List[Review] = field(default_factory=list)
    images: List[Dict[str, str]] = field(default_factory=list)  # lista słowników {url: str, alt: str}
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Nowe pola dodane w ramach rozbudowy
    average_rating: float = 0.0
    sentiment_score: float = 0.0
    seasonal_ratings: Dict[str, float] = field(default_factory=lambda: {
        'wiosna': 0.0, 'lato': 0.0, 'jesień': 0.0, 'zima': 0.0
    })
    aspect_ratings: Dict[str, float] = field(default_factory=lambda: {
        'widoki': 0.0,
        'trudność': 0.0,
        'oznakowanie': 0.0,
        'infrastruktura': 0.0,
        'bezpieczeństwo': 0.0
    })
    
    def add_review(self, review: Review) -> None:
        """Dodaj nową recenzję i zaktualizuj statystyki."""
        self.reviews.append(review)
        self._update_statistics()
    
    def _update_statistics(self) -> None:
        """Zaktualizuj statystyki na podstawie recenzji."""
        if not self.reviews:
            return
            
        # Aktualizacja średniej oceny
        ratings = [r.rating for r in self.reviews if r.rating is not None]
        self.average_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        # Aktualizacja sentymentu
        sentiments = [r.sentiment_score for r in self.reviews]
        self.sentiment_score = sum(sentiments) / len(sentiments)
        
        # Aktualizacja ocen sezonowych
        seasonal_reviews = {
            'wiosna': [], 'lato': [], 'jesień': [], 'zima': []
        }
        
        for review in self.reviews:
            if review.date and review.rating:
                month = review.date.month
                if 3 <= month <= 5:
                    seasonal_reviews['wiosna'].append(review.rating)
                elif 6 <= month <= 8:
                    seasonal_reviews['lato'].append(review.rating)
                elif 9 <= month <= 11:
                    seasonal_reviews['jesień'].append(review.rating)
                else:
                    seasonal_reviews['zima'].append(review.rating)
        
        for season, ratings in seasonal_reviews.items():
            self.seasonal_ratings[season] = sum(ratings) / len(ratings) if ratings else 0.0
        
        # Aktualizacja ocen aspektów
        for aspect in self.aspect_ratings.keys():
            relevant_reviews = [r for r in self.reviews if aspect in r.aspects]
            if relevant_reviews:
                self.aspect_ratings[aspect] = sum(r.aspects[aspect] 
                                                for r in relevant_reviews) / len(relevant_reviews)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuj obiekt na słownik do serializacji."""
        return {
            'name': self.name,
            'description': self.description,
            'difficulty': self.difficulty,
            'distance': self.distance,
            'duration': str(self.duration),
            'elevation_gain': self.elevation_gain,
            'start_point': self.start_point,
            'end_point': self.end_point,
            'category': self.category,
            'coordinates': self.coordinates,
            'points_of_interest': self.points_of_interest,
            'warnings': self.warnings,
            'reviews': [
                {
                    'text': r.text,
                    'rating': r.rating,
                    'date': r.date.isoformat() if r.date else None,
                    'sentiment_score': r.sentiment_score,
                    'aspects': r.aspects
                }
                for r in self.reviews
            ],
            'images': self.images,
            'last_updated': self.last_updated.isoformat(),
            'average_rating': self.average_rating,
            'sentiment_score': self.sentiment_score,
            'seasonal_ratings': self.seasonal_ratings,
            'aspect_ratings': self.aspect_ratings
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Route':
        """Utwórz obiekt Route z słownika."""
        # Konwersja recenzji
        reviews = []
        for review_data in data.get('reviews', []):
            review = Review(
                text=review_data['text'],
                rating=review_data.get('rating'),
                date=datetime.fromisoformat(review_data['date']) if review_data.get('date') else None
            )
            review.sentiment_score = review_data.get('sentiment_score', 0.0)
            review.aspects = review_data.get('aspects', {})
            reviews.append(review)
        
        # Konwersja czasu trwania
        duration_str = data.get('duration', '0:00:00')
        hours, minutes, seconds = map(int, duration_str.split(':'))
        duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        
        # Utworzenie obiektu
        route = cls(
            name=data['name'],
            description=data['description'],
            difficulty=data['difficulty'],
            distance=data['distance'],
            duration=duration,
            elevation_gain=data['elevation_gain'],
            start_point=data['start_point'],
            end_point=data['end_point'],
            category=data['category'],
            coordinates=data['coordinates'],
            points_of_interest=data.get('points_of_interest', []),
            warnings=data.get('warnings', []),
            reviews=reviews,
            images=data.get('images', []),
            last_updated=datetime.fromisoformat(data['last_updated'])
        )
        
        # Dodatkowe pola
        route.average_rating = data.get('average_rating', 0.0)
        route.sentiment_score = data.get('sentiment_score', 0.0)
        route.seasonal_ratings = data.get('seasonal_ratings', {
            'wiosna': 0.0, 'lato': 0.0, 'jesień': 0.0, 'zima': 0.0
        })
        route.aspect_ratings = data.get('aspect_ratings', {
            'widoki': 0.0,
            'trudność': 0.0,
            'oznakowanie': 0.0,
            'infrastruktura': 0.0,
            'bezpieczeństwo': 0.0
        })
        
        return route 