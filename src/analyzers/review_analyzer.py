import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from textblob import TextBlob
from collections import Counter

class Review:
    def __init__(self, text: str, rating: Optional[float] = None, date: Optional[datetime] = None):
        self.text = text
        self.rating = rating
        self.date = date
        self.sentiment_score = 0.0
        self.aspects = {}

class ReviewAnalyzer:
    def __init__(self):
        self.rating_patterns = [
            r'(\d+(?:[.,]\d+)?)\s*/\s*\d+',  
            r'(\d+(?:[.,]\d+)?)\s*gwiazdki?(?:\s+na\s+\d+)?',  
            r'(\d+(?:[.,]\d+)?)\s*punkty?(?:\s+na\s+\d+)?',  
            r'ocena:\s*(\d+(?:[.,]\d+)?)',  
        ]
        
        self.date_patterns = [
            r'(\d{1,2})[./](\d{1,2})[./](\d{2,4})',  
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  
        ]
        
        self.aspect_keywords = {
            'widoki': ['widok', 'panoram', 'krajobraz', 'perspektyw'],
            'trudność': ['trudny', 'łatwy', 'wymagając', 'prosty', 'męczący'],
            'oznakowanie': ['oznakowa', 'szlak', 'znak', 'oznaczen'],
            'infrastruktura': ['ławk', 'parking', 'toalet', 'schronisk'],
            'bezpieczeństwo': ['bezpieczn', 'niebezpiecz', 'zabezpiecz', 'łańcuch'],
        }
        
        self.positive_words = [
            'świetny', 'wspaniały', 'piękny', 'rewelacyjny', 'fantastyczny',
            'polecam', 'super', 'doskonały', 'przyjemny', 'wart', 'dobry'
        ]
        
        self.negative_words = [
            'słaby', 'zły', 'kiepski', 'fatalny', 'niebezpieczny', 'trudny',
            'męczący', 'niewart', 'rozczarowujący', 'niepolecam'
        ]

    def analyze_review(self, review: Review) -> Review:
        
        review.sentiment_score = self._analyze_sentiment(review.text)
        
        if not review.rating:
            review.rating = self._extract_rating(review.text)
        
        if not review.date:
            review.date = self._extract_date(review.text)
        
        review.aspects = self._analyze_aspects(review.text)
        
        return review

    def _analyze_sentiment(self, text: str) -> float:
        
        blob = TextBlob(text.lower())
        base_sentiment = blob.sentiment.polarity

        word_count = len(text.split())
        positive_count = sum(1 for word in self.positive_words if word.lower() in text.lower())
        negative_count = sum(1 for word in self.negative_words if word.lower() in text.lower())
        
        custom_sentiment = (positive_count - negative_count) / (word_count + 1)  
        
        return 0.7 * base_sentiment + 0.3 * custom_sentiment

    def _extract_rating(self, text: str) -> Optional[float]:
        for pattern in self.rating_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return float(match.group(1).replace(',', '.'))
                except ValueError:
                    continue
        return None

    def _extract_date(self, text: str) -> Optional[datetime]:
        for pattern in self.date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    if len(match.groups()) == 3:
                        day, month, year = match.groups()
                        if len(year) == 2:
                            year = '20' + year
                        return datetime(int(year), int(month), int(day))
                except ValueError:
                    continue
        return None

    def _analyze_aspects(self, text: str) -> Dict[str, float]:
        text = text.lower()
        aspects = {}
        
        for aspect, keywords in self.aspect_keywords.items():
            aspect_mentions = sum(text.count(keyword) for keyword in keywords)
            if aspect_mentions > 0:
                aspect_sentiment = 0
                for keyword in keywords:
                    idx = text.find(keyword)
                    if idx != -1:
                        start = max(0, idx - 50)
                        end = min(len(text), idx + 50)
                        context = text[start:end]
                        blob = TextBlob(context)
                        aspect_sentiment += blob.sentiment.polarity
                
                aspects[aspect] = aspect_sentiment / aspect_mentions
                
        return aspects

    def get_seasonal_stats(self, reviews: List[Review]) -> Dict[str, float]:
        seasonal_ratings = {
            'wiosna': [], 'lato': [], 'jesień': [], 'zima': []
        }
        
        for review in reviews:
            if review.date and review.rating:
                month = review.date.month
                if 3 <= month <= 5:
                    seasonal_ratings['wiosna'].append(review.rating)
                elif 6 <= month <= 8:
                    seasonal_ratings['lato'].append(review.rating)
                elif 9 <= month <= 11:
                    seasonal_ratings['jesień'].append(review.rating)
                else:
                    seasonal_ratings['zima'].append(review.rating)
        
        return {
            season: sum(ratings)/len(ratings) if ratings else 0.0
            for season, ratings in seasonal_ratings.items()
        }

    def get_most_mentioned_aspects(self, reviews: List[Review], top_n: int = 5) -> List[Tuple[str, int]]:
        aspect_counts = Counter()
        
        for review in reviews:
            for aspect in review.aspects.keys():
                aspect_counts[aspect] += 1
                
        return aspect_counts.most_common(top_n) 