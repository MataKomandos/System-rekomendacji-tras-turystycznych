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
        # Konfiguracja stylu wykresów
        plt.rcParams['figure.figsize'] = (10, 4)
        plt.rcParams['font.size'] = 10
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['axes.titlesize'] = 14
        
        # Polskie nazwy miesięcy
        self.months = ['Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
                      'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień']

    def create_route_comparison_chart(self, routes: List[Dict[str, Any]], 
                                   param: str = 'length') -> BytesIO:
        """Tworzy wykres słupkowy porównujący parametry tras.
        
        Args:
            routes: Lista słowników zawierających dane tras
            param: Parametr do porównania (domyślnie długość trasy)
            
        Returns:
            BytesIO: Bufor zawierający wygenerowany wykres
        """
        plt.figure(figsize=(12, 6))
        
        # Przygotuj dane
        names = []
        values = []
        for route in routes:
            # Sprawdź różne możliwe nazwy parametru długości
            if param == 'length':
                value = route.get('length') or route.get('distance') or route.get('długość') or 0
            else:
                value = route.get(param, 0)
            
            if value != 0:  # Dodaj tylko trasy z niezerowymi wartościami
                names.append(route.get('name', 'Nieznana trasa'))
                values.append(value)
        
        if not names:  # Jeśli nie ma danych, dodaj przykładowe
            names = ['Przykładowa trasa 1', 'Przykładowa trasa 2', 'Przykładowa trasa 3']
            values = [10, 15, 8]
        
        # Utwórz wykres słupkowy
        bars = plt.bar(names, values)
        
        # Dodaj etykiety z wartościami nad słupkami
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}',
                    ha='center', va='bottom')
        
        # Dostosuj wygląd
        plt.title(f'Porównanie tras - {param}')
        plt.xlabel('Nazwa trasy')
        plt.ylabel('Długość [km]' if param == 'length' else param)
        plt.xticks(rotation=45, ha='right')
        
        # Dodaj siatkę
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        # Dostosuj marginesy
        plt.tight_layout()
        
        # Zapisz wykres do bufora
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=300)
        plt.close()
        img_buffer.seek(0)
        
        return img_buffer

    def create_category_distribution_pie(self, routes: List[Dict[str, Any]]) -> BytesIO:
        """Tworzy wykres kołowy pokazujący rozkład kategorii tras."""
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
        """Tworzy wykres profilu wysokościowego trasy."""
        # Przygotuj dane
        distances = [point[0] for point in elevation_data]
        elevations = [point[1] for point in elevation_data]
        
        # Utwórz nowy wykres
        fig, ax = plt.subplots()
        
        # Narysuj profil wysokościowy
        ax.plot(distances, elevations, 'b-', linewidth=2)
        ax.fill_between(distances, elevations, min(elevations), alpha=0.1, color='blue')
        
        # Dodaj etykiety i tytuł
        ax.set_xlabel('Dystans [km]')
        ax.set_ylabel('Wysokość [m n.p.m.]')
        ax.set_title('Profil wysokościowy trasy')
        
        # Dodaj siatkę
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Zapisz wykres do bufora
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Przewiń bufor na początek
        buffer.seek(0)
        return buffer

    def create_popularity_heatmap(self, popularity_data: Dict[str, Dict[str, int]]) -> BytesIO:
        """Tworzy mapę ciepła pokazującą popularność tras w różnych miesiącach.
        
        Args:
            popularity_data: Słownik zawierający dane o popularności tras w poszczególnych miesiącach
                           Format: {'nazwa_trasy': {'1': wartość_stycznia, '2': wartość_lutego, ...}}
        
        Returns:
            BytesIO: Bufor zawierający wygenerowany wykres
        """
        # Przygotuj dane do mapy ciepła
        routes = list(popularity_data.keys())
        data = np.zeros((len(routes), 12))
        
        for i, route in enumerate(routes):
            for month, count in popularity_data[route].items():
                data[i, int(month)-1] = count
        
        plt.figure(figsize=(15, max(6, len(routes) * 0.4)))
        
        # Utwórz mapę ciepła
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
        
        # Zapisz wykres do bufora
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=300)
        plt.close()
        img_buffer.seek(0)
        
        return img_buffer

    def create_route_radar_chart(self, 
                               route_ratings: Dict[str, float],
                               max_value: float = 5.0) -> BytesIO:
        """Tworzy wykres radarowy oceniający trasę pod różnymi względami."""
        categories = list(route_ratings.keys())
        values = list(route_ratings.values())
        
        # Dodaj pierwszy punkt na końcu aby zamknąć wielokąt
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
        """Tworzy interaktywną mapę trasy z punktami POI."""
        if not route_points:
            return ""
            
        # Znajdź środek trasy dla początkowego widoku
        center_lat = sum(point[0] for point in route_points) / len(route_points)
        center_lon = sum(point[1] for point in route_points) / len(route_points)
        
        # Utwórz mapę
        m = folium.Map(location=[center_lat, center_lon], zoom_start=13)
        
        # Dodaj trasę
        points = [[point[0], point[1]] for point in route_points]
        folium.PolyLine(points, weight=3, color='red', opacity=0.8).add_to(m)
        
        # Dodaj markery startu i mety
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
        
        # Dodaj punkty POI jeśli są dostępne
        if points_of_interest:
            for poi in points_of_interest:
                folium.Marker(
                    [poi['lat'], poi['lon']],
                    popup=poi['name'],
                    icon=folium.Icon(color='orange', icon='info-sign')
                ).add_to(m)
        
        # Dodaj plugin do pomiaru odległości
        plugins.MeasureControl(position='topleft').add_to(m)
        
        # Dodaj mini-mapę
        plugins.MiniMap().add_to(m)
        
        # Zapisz mapę do pliku HTML
        output_file = f'data/maps/route_map_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        m.save(output_file)
        
        return output_file

    def create_difficulty_distribution(self, routes: List[Dict[str, Any]]) -> BytesIO:
        """Tworzy wykres pokazujący rozkład trudności tras."""
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
        """Tworzy histogram czasów przejścia tras."""
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
        """Tworzy wykres kołowy pokazujący rozkład kategorii tras.
        
        Args:
            routes: Lista słowników zawierających dane tras
            
        Returns:
            BytesIO: Bufor zawierający wygenerowany wykres
        """
        # Zbierz kategorie i policz ich wystąpienia
        categories = {}
        for route in routes:
            category = route.get('category', 'Inna')
            categories[category] = categories.get(category, 0) + 1
            
        # Przygotuj dane do wykresu
        labels = list(categories.keys())
        sizes = list(categories.values())
        
        # Zdefiniuj kolory dla wykresu
        colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99CC', '#99CCFF', '#FFB366', '#FF99FF']
        
        # Utwórz wykres
        plt.figure(figsize=(10, 8))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', 
                shadow=True, startangle=90, colors=colors)
        
        plt.title('Rozkład kategorii tras')
        plt.axis('equal')  # Równe proporcje zapewniają kołowy kształt
        
        # Dodaj legendę
        plt.legend(labels, title="Kategorie", 
                  loc="center left", 
                  bbox_to_anchor=(1, 0, 0.5, 1))
        
        # Zapisz wykres do bufora
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        plt.close()
        img_buffer.seek(0)
        
        return img_buffer

    def create_route_radar_evaluation(self, route_data: Dict[str, float]) -> BytesIO:
        """Tworzy wykres radarowy oceniający trasę pod różnymi kryteriami.
        
        Args:
            route_data: Słownik zawierający oceny trasy w różnych kategoriach
                       (np. {'trudność': 4.5, 'widoki': 5.0, 'dostępność': 3.0})
            
        Returns:
            BytesIO: Bufor zawierający wygenerowany wykres
        """
        # Przygotuj dane
        categories = list(route_data.keys())
        values = list(route_data.values())
        
        # Liczba kategorii
        num_vars = len(categories)
        
        # Oblicz kąty dla każdej osi (w radianach)
        angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
        
        # Domknij wykres przez powtórzenie pierwszej wartości
        values += values[:1]
        angles += angles[:1]
        
        # Inicjalizuj wykres
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Narysuj wykres
        ax.plot(angles, values, 'o-', linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        
        # Ustaw etykiety
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        
        # Ustaw zakres wartości (0-5)
        ax.set_ylim(0, 5)
        
        # Dodaj tytuł
        plt.title('Ocena trasy w różnych kategoriach', y=1.05)
        
        # Dodaj siatkę
        ax.grid(True)
        
        # Zapisz wykres do bufora
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        plt.close()
        img_buffer.seek(0)
        
        return img_buffer 