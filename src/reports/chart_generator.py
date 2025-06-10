import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from io import BytesIO
import calendar
from datetime import datetime
import folium
from folium import plugins

class ChartGenerator:
    def __init__(self):
        plt.rcParams['figure.figsize'] = (10, 4)
        plt.rcParams['font.size'] = 10
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['axes.titlesize'] = 14
        
        self.months = ['Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
                      'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień']

    def create_route_comparison_chart(self, routes: List[Dict[str, Any]], 
                                   param: str = 'length') -> BytesIO:
        
        plt.figure(figsize=(12, 6))
        
        names = []
        values = []
        for route in routes:
            if param == 'length':
                value = route.get('length') or route.get('distance') or route.get('długość') or 0
            else:
                value = route.get(param, 0)
            
            if value != 0:  
                names.append(route.get('name', 'Nieznana trasa'))
                values.append(value)
        
        if not names:  
            names = ['Przykładowa trasa 1', 'Przykładowa trasa 2', 'Przykładowa trasa 3']
            values = [10, 15, 8]
        
        bars = plt.bar(names, values)
        
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom')
        
        plt.title(f'Porównanie tras - {param}')
        plt.xlabel('Nazwa trasy')
        plt.ylabel('Długość [km]' if param == 'length' else param)
        plt.xticks(rotation=45, ha='right')
        
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=300)
        plt.close()
        img_buffer.seek(0)
        
        return img_buffer

    def create_category_distribution_pie(self, routes: List[Dict[str, Any]]) -> BytesIO:
        
        categories = {}
        for route in routes:
            category = route.get('category', 'Inne')
            categories[category] = categories.get(category, 0) + 1
        
        plt.figure(figsize=(10, 10))
        plt.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%',
                shadow=True, startangle=90)
        plt.title('Rozkład kategorii tras')
        plt.axis('equal')
        
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        plt.close()
        img_buffer.seek(0)
        
        return img_buffer

    def create_elevation_profile(self, elevation_data: List[Tuple[float, float]]) -> BytesIO:
        
        distances = [point[0] for point in elevation_data]
        elevations = [point[1] for point in elevation_data]
        
        fig, ax = plt.subplots()
        
        ax.plot(distances, elevations, 'b-', linewidth=2)
        ax.fill_between(distances, elevations, min(elevations), alpha=0.1, color='blue')
        
        ax.set_xlabel('Dystans [km]')
        ax.set_ylabel('Wysokość [m n.p.m.]')
        ax.set_title('Profil wysokościowy trasy')
        
        ax.grid(True, linestyle='--', alpha=0.7)
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        
        buffer.seek(0)
        return buffer

    def create_popularity_heatmap(self, popularity_data: Dict[str, Dict[str, int]]) -> BytesIO:
        
        routes = list(popularity_data.keys())
        data = np.zeros((len(routes), 12))
        
        for i, route in enumerate(routes):
            for month, count in popularity_data[route].items():
                data[i, int(month)-1] = count
        
        plt.figure(figsize=(15, max(6, len(routes) * 0.4)))
        
        sns.heatmap(data, 
                   xticklabels=self.months,
                   yticklabels=routes,
                   cmap='YlOrRd',
                   annot=True,
                   fmt='.0f',
                   cbar_kws={'label': 'Popularność (%)'},
                   vmin=0,
                   vmax=100)
        
        plt.title('Popularność tras w poszczególnych miesiącach')
        plt.xlabel('Miesiąc')
        plt.ylabel('Trasa')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=300)
        plt.close()
        img_buffer.seek(0)
        
        return img_buffer

    def create_route_radar_chart(self, 
                               route_ratings: Dict[str, float],
                               max_value: float = 5.0) -> BytesIO:
        
        categories = list(route_ratings.keys())
        values = list(route_ratings.values())
        
        values += values[:1]
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))  # Zamknij wykres
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        ax.plot(angles, values)
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, max_value)
        
        plt.title('Ocena trasy w różnych kategoriach')
        
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        plt.close()
        img_buffer.seek(0)
        
        return img_buffer

    def create_route_map(self, 
                        route_points: List[Tuple[float, float]],
                        points_of_interest: Optional[List[Dict[str, Any]]] = None) -> str:
        
        if not route_points:
            return ""
            
        center_lat = sum(point[0] for point in route_points) / len(route_points)
        center_lon = sum(point[1] for point in route_points) / len(route_points)
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
        
        points = [[point[0], point[1]] for point in route_points]
        folium.PolyLine(points, weight=3, color='blue', opacity=0.8).add_to(m)
        
        folium.Marker(
            points[0],
            popup='Start',
            icon=folium.Icon(color='green', icon='info-sign')
        ).add_to(m)
        
        folium.Marker(
            points[-1],
            popup='Meta',
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        
        if points_of_interest:
            for poi in points_of_interest:
                folium.Marker(
                    [poi['lat'], poi['lon']],
                    popup=poi['name'],
                    icon=folium.Icon(color='orange', icon='info-sign')
                ).add_to(m)
        
        plugins.MeasureControl(position='topleft').add_to(m)
        
        plugins.MiniMap().add_to(m)
        
        output_file = f'data/maps/route_map_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        m.save(output_file)
        
        return output_file

    def create_difficulty_distribution(self, routes: List[Dict[str, Any]]) -> BytesIO:

        difficulties = {}
        for route in routes:
            difficulty = route.get('difficulty', 'Nieznana')
            difficulties[difficulty] = difficulties.get(difficulty, 0) + 1
        
        plt.figure(figsize=(10, 6))
        colors = ['green', 'yellow', 'red', 'gray']
        plt.bar(difficulties.keys(), difficulties.values(), color=colors[:len(difficulties)])
        
        plt.title('Rozkład trudności tras')
        plt.xlabel('Poziom trudności')
        plt.ylabel('Liczba tras')
        
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        plt.close()
        img_buffer.seek(0)
        
        return img_buffer

    def create_duration_histogram(self, routes: List[Dict[str, Any]]) -> BytesIO:
        
        durations = [route.get('duration', 0) for route in routes if route.get('duration')]
        
        plt.figure(figsize=(10, 6))
        plt.hist(durations, bins=20, edgecolor='black')
        plt.title('Rozkład czasów przejścia tras')
        plt.xlabel('Czas przejścia [h]')
        plt.ylabel('Liczba tras')
        
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        plt.close()
        img_buffer.seek(0)
        
        return img_buffer

    def create_route_categories_pie(self, routes: List[Dict[str, Any]]) -> BytesIO:
        
        categories = {}
        for route in routes:
            category = route.get('category', 'Inna')
            categories[category] = categories.get(category, 0) + 1
            
        labels = list(categories.keys())
        sizes = list(categories.values())
        
        
        plt.figure(figsize=(10, 8))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', 
                shadow=True, startangle=90)
        
        plt.title('Rozkład kategorii tras')
        plt.axis('equal') 
        
        plt.legend(labels, title="Kategorie", 
                  loc="center left", 
                  bbox_to_anchor=(1, 0, 0.5, 1))
        
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        plt.close()
        img_buffer.seek(0)
        
        return img_buffer

    def create_route_radar_evaluation(self, route_data: Dict[str, float]) -> BytesIO:
            
        categories = list(route_data.keys())
        values = list(route_data.values())
        
        num_vars = len(categories)
        
        angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
        
        values += values[:1]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        ax.plot(angles, values, 'o-', linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        
        ax.set_ylim(0, 5)
        
        plt.title('Ocena trasy w różnych kategoriach', y=1.05)
        
        ax.grid(True)
        
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        plt.close()
        img_buffer.seek(0)
        
        return img_buffer 