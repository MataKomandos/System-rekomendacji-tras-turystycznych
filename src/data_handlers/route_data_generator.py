import numpy as np
from typing import List, Tuple, Dict, Any

class RouteDataGenerator:
    def __init__(self):
        self.region_elevation_ranges = {
            'Tatry': (800, 2500),
            'Pieniny': (400, 1000),
            'Góry Stołowe': (500, 900),
            'Sudety': (500, 1600),
            'Dolny Śląsk': (300, 800),
            'Mazowieckie': (100, 200),
            'Pomorze': (0, 50)
        }

    def generate_elevation_profile(self, route: Dict[str, Any]) -> List[Tuple[float, float]]:
        
        region = route['region']
        
        if 'distance' in route:
            distance = route['distance']
        else:
            distance = route['czas_h'] * 3  
        
        min_elevation, max_elevation = self.region_elevation_ranges.get(
            region, (0, 500)  
        )
        
        num_points = int(distance * 10) + 1
        
        x = np.linspace(0, distance, num_points)
        
        if region in ['Tatry', 'Sudety', 'Pieniny']:
            num_peaks = int(distance / 2)  
            y_base = np.zeros(num_points)
            for i in range(num_peaks):
                phase = 2 * np.pi * i / num_peaks
                amplitude = np.random.uniform(0.3, 1.0)
                y_base += amplitude * np.sin(2 * np.pi * x / distance + phase)
            
            y_base = (y_base - y_base.min()) / (y_base.max() - y_base.min())
            elevations = min_elevation + y_base * (max_elevation - min_elevation)
            
        elif region in ['Góry Stołowe', 'Dolny Śląsk']:
            num_peaks = int(distance / 3)  
            y_base = np.zeros(num_points)
            for i in range(num_peaks):
                phase = 2 * np.pi * i / num_peaks
                amplitude = np.random.uniform(0.2, 0.8)
                y_base += amplitude * np.sin(2 * np.pi * x / distance + phase)
            
            y_base = (y_base - y_base.min()) / (y_base.max() - y_base.min())
            elevations = min_elevation + y_base * (max_elevation - min_elevation)
            
        else:
            y_base = np.random.normal(0.5, 0.1, num_points)
            y_base = np.clip(y_base, 0, 1)
            elevations = min_elevation + y_base * (max_elevation - min_elevation)
        
        noise = np.random.normal(0, (max_elevation - min_elevation) * 0.02, num_points)
        elevations += noise
        
        elevations = np.round(elevations)
        
        return list(zip(x.tolist(), elevations.tolist()))

    def add_elevation_data_to_routes(self, routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            
        for route in routes:
            route['elevation_data'] = self.generate_elevation_profile(route)
        return routes 