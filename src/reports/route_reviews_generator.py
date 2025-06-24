import os
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from bs4 import BeautifulSoup
import re

class RouteReviewsGenerator:
    def __init__(self, output_dir: str = 'data/route_reviews'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_route_html(self, route: Dict[str, Any], index: int) -> str:
        html_content = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Opinia o trasie: {route.get('name', 'Nieznana trasa')}</title>
    <style>
        .route-info {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }}
        .route-params {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        .route-params td {{
            padding: 8px;
            border: 1px solid #ddd;
        }}
        .route-params td:first-child {{
            font-weight: bold;
            width: 200px;
        }}
        .user-review {{
            margin-top: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }}
        .rating {{
            color: #ffd700;
            font-size: 20px;
        }}
    </style>
</head>
<body>
    <div class="route-info">
        <h2>{route.get('name', 'Nieznana trasa')}</h2>
        <table class="route-params">
            <tr><td>Długość:</td><td>{route.get('length') or route.get('distance') or route.get('długość') or 'b/d'} km</td></tr>
            <tr><td>Czas przejścia:</td><td>{route.get('duration', 'b/d')}</td></tr>
            <tr><td>Przewyższenie:</td><td>{route.get('elevation', 'b/d')} m</td></tr>
            <tr><td>Trudność:</td><td>{route.get('difficulty', 'b/d')}</td></tr>
            <tr><td>Zalecana pora:</td><td>{route.get('recommended_time', 'b/d')}</td></tr>
        </table>
        <div class="user-review">
            <span class="rating">{'★' * int(route.get('rating', 0))}</span>
            <p>{route.get('review', 'Brak opinii.')}</p>
            {f'<p><small>Data opinii: {route.get("review_date", "")}</small></p>' if route.get('review_date') else ''}
        </div>
    </div>
</body>
</html>"""
        
        filename = os.path.join(self.output_dir, f"route_{index}.html")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        metadata = {
            'route_name': route.get('name', 'Nieznana trasa'),
            'generated_at': datetime.now().isoformat(),
            'parameters': {
                'length': route.get('length') or route.get('distance') or route.get('długość'),
                'duration': route.get('duration'),
                'elevation': route.get('elevation'),
                'difficulty': route.get('difficulty'),
                'rating': route.get('rating', 0),
                'recommended_time': route.get('recommended_time')
            }
        }
        
        json_filename = os.path.join(self.output_dir, f"route_{index}_meta.json")
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        
        return filename
    
    def generate_all_reviews(self, routes_data: List[Dict[str, Any]]) -> List[str]:
        generated_files = []
        for i, route in enumerate(routes_data, 1):
            html_file = self.generate_route_html(route, i)
            generated_files.append(html_file)
        return generated_files
    
    def get_route_analysis(self, route: Dict[str, Any]) -> Dict[str, str]:
        duration = route.get('duration', '')
        if isinstance(duration, str):
            time_str = duration
        else:
            time_str = "nie określono"

        elevation = route.get('elevation', '')
        if elevation:
            elevation_str = str(elevation)
        else:
            elevation_str = "nie określono"
        
        difficulty = route.get('difficulty', '')
        
        if isinstance(difficulty, (int, float)):
            if difficulty <= 2:
                difficulty = 'łatwa'
            elif difficulty <= 3.5:
                difficulty = 'średnia'
            else:
                difficulty = 'trudna'
        else:
            difficulty = str(difficulty).lower()
            if 'łatwa' in difficulty or 'easy' in difficulty or '1' in difficulty or '2' in difficulty:
                difficulty = 'łatwa'
            elif 'średnia' in difficulty or 'średnio' in difficulty or 'medium' in difficulty or '3' in difficulty:
                difficulty = 'średnia'
            elif 'trudna' in difficulty or 'hard' in difficulty or '4' in difficulty or '5' in difficulty:
                difficulty = 'trudna'
            else:
                difficulty = str(route.get('difficulty', 'nieznana'))

        if ':' in str(duration):
            try:
                hours = float(duration.split(':')[0])
                if hours > 4:
                    recommended_time = "wczesny ranek"
                elif hours > 2:
                    recommended_time = "rano lub popołudnie"
                else:
                    recommended_time = "dowolna pora dnia"
            except:
                recommended_time = "nie określono"
        else:
            recommended_time = "nie określono"
        
        return {
            "Trudność": difficulty,
            "Czas": time_str,
            "Przewyższenie": elevation_str,
            "Zalecana pora": recommended_time,
            "Ostrzeżenia": route.get('warnings', 'brak')
        }

    def get_html_content(self, index: int) -> str:
        try:
            with open(os.path.join(self.output_dir, f"route_{index}.html"), 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def read_route_reviews(self, route_id: int) -> Optional[Dict[str, Any]]:
        try:
            html_content = self.get_html_content(route_id)
            if not html_content:
                return None
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            route_data = {}
            
            route_data['name'] = soup.find('h2').text.strip()
            
            params_table = soup.find('table', class_='route-params')
            if params_table:
                for row in params_table.find_all('tr'):
                    cells = row.find_all('td')
                    if len(cells) == 2:
                        key = cells[0].text.strip(':')
                        value = cells[1].text.strip()
                        route_data[key.lower()] = value
            
            reviews_div = soup.find('div', class_='user-review')
            if reviews_div:
                rating_span = reviews_div.find('span', class_='rating')
                if rating_span:
                    route_data['rating'] = len(rating_span.text.strip())
                
                review_text = reviews_div.find('p')
                if review_text:
                    route_data['review'] = review_text.text.strip()
                
                review_date = reviews_div.find('small')
                if review_date:
                    date_text = review_date.text.strip()
                    date_match = re.search(r'Data opinii: (.+)', date_text)
                    if date_match:
                        route_data['review_date'] = date_match.group(1)
            
            return route_data
        except Exception as e:
            print(f"Błąd podczas odczytu recenzji dla trasy {route_id}: {str(e)}")
            return None

    def get_route_data(self, route: Dict[str, Any]) -> Dict[str, Any]:
        route_data = {
            'name': route.get('name', 'Nieznana trasa'),
            'length': route.get('length') or route.get('distance') or route.get('długość') or 'b/d',
            'duration': route.get('duration', 'b/d'),
            'elevation': route.get('elevation', 'b/d'),
            'difficulty': route.get('difficulty', 'b/d'),
            'rating': route.get('rating', 0),
            'reviews': []
        }
        
        if 'review' in route:
            route_data['reviews'].append({
                'author': route.get('author', 'Anonim'),
                'date': route.get('review_date', datetime.now().strftime('%Y-%m-%d')),
                'text': route['review'],
                'rating': route.get('rating', 0)
            })
        
        return route_data