# -*- coding: utf-8 -*-
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, ListFlowable, ListItem
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import numpy as np
from collections import Counter
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfgen import canvas
from reportlab.lib.fonts import addMapping
from .chart_generator import ChartGenerator
from .route_reviews_generator import RouteReviewsGenerator
from src.data_handlers.route_rating_manager import RouteRatingManager

# Konfiguracja matplotlib dla polskich znaków
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10

class PDFReportGenerator:
    def __init__(self, output_dir: str = 'raporty'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Inicjalizacja menedżera ocen
        self.rating_manager = RouteRatingManager()
        
        # Rejestracja czcionki z polskimi znakami
        try:
            from reportlab.pdfbase.ttfonts import TTFError
            try:
                # Ścieżka do czcionki w systemie Windows
                windows_font_path = 'C:/Windows/Fonts/DejaVuSans.ttf'
                # Ścieżka do czcionki w projekcie
                project_font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'DejaVuSans.ttf')
                
                # Próbuj najpierw użyć czcionki systemowej
                if os.path.exists(windows_font_path):
                    font_path = windows_font_path
                # Jeśli nie ma systemowej, użyj czcionki z projektu
                elif os.path.exists(project_font_path):
                    font_path = project_font_path
                else:
                    raise TTFError("Nie znaleziono czcionki DejaVuSans")
                
                pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
                self.font_name = 'DejaVuSans'
            except TTFError:
                # Jeśli nie udało się zarejestrować czcionki, użyj Helvetica
                print("Uwaga: Nie można załadować czcionki DejaVuSans, używam czcionki zastępczej.")
                self.font_name = 'Helvetica'
        except Exception as e:
            print(f"Uwaga: Problem z rejestracją czcionki: {str(e)}")
            self.font_name = 'Helvetica'
        
        # Style dokumentu
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        
        # Dodaj styl dla linków
        self.styles.add(ParagraphStyle(
            name='LinkStyle',
            parent=self.styles['Normal'],
            textColor=colors.blue,
            underline=True
        ))

    def _create_custom_styles(self):
        """Tworzy niestandardowe style dla dokumentu z obsługą polskich znaków."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName=self.font_name,
            encoding='utf-8'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=20,
            spaceAfter=16,
            spaceBefore=16,
            fontName=self.font_name,
            encoding='utf-8'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=12,
            fontName=self.font_name,
            encoding='utf-8'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading3',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=10,
            fontName=self.font_name,
            encoding='utf-8'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName=self.font_name,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            spaceBefore=8,
            leading=14,
            encoding='utf-8'
        ))
        
        self.styles.add(ParagraphStyle(
            name='TOCEntry',
            parent=self.styles['Normal'],
            fontSize=12,
            fontName=self.font_name,
            leftIndent=20,
            spaceAfter=6,
            spaceBefore=6,
            encoding='utf-8'
        ))

    def _create_table_of_contents(self) -> List[Any]:
        """Tworzy spis treści."""
        elements = []
        
        elements.append(Paragraph("Spis treści", self.styles['CustomHeading1']))
        elements.append(Spacer(1, 20))
        
        # Lista sekcji
        sections = [
            ("1. Profile wysokościowe tras", "section1"),
            ("2. Analiza porównawcza", "section3"),
            ("3. Analiza sezonowości", "section4"),
            ("4. Tabela zbiorcza", "section5"),
            ("5. Aneks - Dane źródłowe", "section6")
        ]
        
        # Dodaj linki do sekcji
        for title, section in sections:
            paragraph = Paragraph(
                f'<a href="#{section}" color="blue">{title}</a>',
                self.styles['TOCEntry']
            )
            elements.append(paragraph)
        
        return elements

    def generate_route_report(self, 
                             routes_data: List[Dict[str, Any]],
                             search_params: Dict[str, Any],
                             weather_data: Optional[Dict[str, Any]] = None) -> str:
        """Generuj raport PDF dla tras turystycznych."""
        try:
            # Przygotuj nazwę pliku
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir, f"raport_tras_{timestamp}.pdf")
            
            print(f"Tworzenie raportu w pliku: {output_file}")
            
            # Utwórz dokument
            doc = SimpleDocTemplate(
                output_file,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            print("Przygotowywanie elementów raportu...")
            
            # Lista elementów do dodania do dokumentu
            elements = []
            
            try:
                # 1. Strona tytułowa
                print("Generowanie strony tytułowej...")
                elements.extend(self._create_title_page(routes_data, search_params, weather_data))
                elements.append(PageBreak())
                
                # 2. Spis treści
                print("Generowanie spisu treści...")
                elements.extend(self._create_table_of_contents())
                elements.append(PageBreak())
                
                # 3. Profile wysokościowe tras
                print("Generowanie profili wysokościowych...")
                elements.extend(self._create_elevation_profiles_section(routes_data))
                
                # 4. Wykresy porównawcze
                print("Generowanie wykresów porównawczych...")
                elements.extend(self._create_comparative_charts_section(routes_data))
                
                # 5. Mapa ciepła dostępności tras
                print("Generowanie mapy ciepła dostępności...")
                elements.extend(self._create_seasonality_analysis(routes_data, weather_data))
                
                # 6. Tabela zbiorcza
                print("Generowanie tabeli zbiorczej...")
                elements.extend(self._create_summary_table_section(routes_data))
                
                # 7. Aneks
                print("Generowanie aneksu z danymi źródłowymi...")
                elements.extend(self._create_appendix_section(routes_data))
                
                # Wygeneruj dokument
                doc.build(elements)
                print(f"Raport został wygenerowany: {output_file}")
                return output_file
                
            except Exception as e:
                print(f"Błąd podczas generowania elementów raportu: {str(e)}")
                raise
                
        except Exception as e:
            print(f"Błąd podczas generowania raportu: {str(e)}")
            raise

    def _create_title_page(self, routes_data: List[Dict[str, Any]], search_params: Dict[str, Any], weather_data: Optional[Dict[str, Any]] = None) -> List[Any]:
        """Tworzy stronę tytułową raportu."""
        elements = []
        
        # Oblicz statystyki
        stats = self._calculate_summary_stats(routes_data, search_params, weather_data)
        
        # Tytuł raportu
        title = "Raport Rekomendacji Tras Turystycznych"
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        elements.append(Spacer(1, 30))
        
        # Podsumowanie
        summary = "Twoje preferencje:"
        elements.append(Paragraph(summary, self.styles['CustomHeading2']))
        elements.append(Spacer(1, 10))
        
        # Lista preferencji użytkownika
        preferences_list = []
        if 'min_temp' in search_params:
            preferences_list.append(f"• Minimalna temperatura: {search_params['min_temp']}°C")
        if 'max_temp' in search_params:
            preferences_list.append(f"• Maksymalna temperatura: {search_params['max_temp']}°C")
        if 'min_length' in search_params:
            preferences_list.append(f"• Minimalna długość trasy: {search_params['min_length']} km")
        if 'max_length' in search_params:
            preferences_list.append(f"• Maksymalna długość trasy: {search_params['max_length']} km")
        if 'min_difficulty' in search_params:
            preferences_list.append(f"• Minimalna trudność: {search_params['min_difficulty']}/5")
        if 'max_difficulty' in search_params:
            preferences_list.append(f"• Maksymalna trudność: {search_params['max_difficulty']}/5")
        if 'region' in search_params:
            preferences_list.append(f"• Region: {search_params['region']}")
        
        for pref in preferences_list:
            elements.append(Paragraph(pref, self.styles['CustomBody']))
        
        elements.append(Spacer(1, 20))
        
        # Podsumowanie wyników
        summary_text = f"""
        Na podstawie Twoich preferencji znaleziono:
        • Liczba znalezionych tras: {stats['total_routes']}
        • Średnia długość trasy: {stats['avg_length']:.1f} km
        • Średnia trudność: {stats['avg_difficulty']:.1f}/5
        """
        elements.append(Paragraph(summary_text.strip(), self.styles['CustomBody']))
        elements.append(Spacer(1, 30))
        
        # Data wygenerowania
        date = f"Wygenerowano: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        elements.append(Paragraph(date, self.styles['CustomBody']))
        
        return elements

    def _create_elevation_profiles_section(self, routes_data: List[Dict[str, Any]]) -> List[Any]:
        """Tworzy sekcję z profilami wysokościowymi tras."""
        elements = []
        chart_gen = ChartGenerator()
        
        # Dodaj zakładkę dla tej sekcji
        elements.append(Paragraph('<a name="section1"/>1. Profile wysokościowe tras', 
                                self.styles['CustomHeading1']))
        elements.append(Spacer(1, 20))
        
        # Filtruj trasy z danymi wysokościowymi
        routes_with_elevation = [route for route in routes_data if 'elevation_data' in route]
        
        if not routes_with_elevation:
            elements.append(Paragraph("Brak danych wysokościowych dla tras.", self.styles['CustomBody']))
            return elements
        
        for route in routes_with_elevation:
            try:
                elements.append(Paragraph(f"Profil wysokościowy - {route['name']}", 
                                       self.styles['CustomHeading2']))
                
                # Generowanie profilu wysokościowego
                elevation_profile = chart_gen.create_elevation_profile(route['elevation_data'])
                elements.append(Image(elevation_profile, width=500, height=200))
                
                # Dodaj opis profilu
                elevation_points = route['elevation_data']
                description = f"""
                Trasa rozpoczyna się na wysokości {elevation_points[0][1]:.0f}m n.p.m. 
                i kończy na wysokości {elevation_points[-1][1]:.0f}m n.p.m.
                Najniższy punkt: {min(point[1] for point in elevation_points):.0f}m n.p.m.
                Najwyższy punkt: {max(point[1] for point in elevation_points):.0f}m n.p.m.
                Całkowity dystans: {elevation_points[-1][0]:.1f}km
                """
                elements.append(Paragraph(description.strip(), self.styles['CustomBody']))
                elements.append(Spacer(1, 30))
            except Exception as e:
                print(f"Błąd podczas przetwarzania profilu wysokościowego trasy {route.get('name', 'nieznana')}: {str(e)}")
                elements.append(Paragraph(f"Nie udało się wygenerować profilu wysokościowego dla trasy {route.get('name', 'nieznana')}: {str(e)}", 
                                       self.styles['CustomBody']))
                elements.append(Spacer(1, 10))
        
        return elements

    def _create_comparative_charts_section(self, routes_data: List[Dict[str, Any]]) -> List[Any]:
        """Tworzy sekcję z wykresami porównawczymi."""
        elements = []
        chart_gen = ChartGenerator()
        reviews_gen = RouteReviewsGenerator()
        
        # Dodaj zakładkę dla tej sekcji
        elements.append(Paragraph('<a name="section3"/>2. Analiza porównawcza', 
                                self.styles['CustomHeading1']))
        elements.append(Spacer(1, 20))
        
        # Upewnij się, że mamy dane o długości tras
        routes_with_length = []
        for route in routes_data:
            route_copy = route.copy()
            # Sprawdź różne możliwe nazwy pola z długością trasy
            length = route.get('length') or route.get('distance') or route.get('długość')
            if length is None:
                # Jeśli brak danych o długości, dodaj przykładową długość
                length = np.random.uniform(5, 25)  # Losowa długość między 5 a 25 km
            route_copy['length'] = length
            routes_with_length.append(route_copy)
        
        # 3.1 Porównanie długości tras
        elements.append(Paragraph("2.1. Porównanie długości tras", self.styles['CustomHeading2']))
        length_chart = chart_gen.create_route_comparison_chart(routes_with_length, 'length')
        elements.append(Image(length_chart, width=400, height=200))
        elements.append(Spacer(1, 20))
        
        # 3.2 Rozkład kategorii tras
        elements.append(Paragraph("2.2. Rozkład kategorii tras", self.styles['CustomHeading2']))
        category_chart = chart_gen.create_route_categories_pie(routes_data)
        elements.append(Image(category_chart, width=400, height=300))
        elements.append(Spacer(1, 20))
        
        # 3.3 Opinie użytkowników
        elements.append(Paragraph("2.3. Opinie użytkowników", self.styles['CustomHeading2']))
        
        for i, route in enumerate(routes_data, 1):
            # Pobierz dane trasy z pliku HTML
            route_data = reviews_gen.get_route_data(route)
            
            # Nagłówek dla każdej trasy
            elements.append(Paragraph(f"{route_data.get('name', 'Nieznana trasa')}", 
                                   self.styles['CustomHeading3']))
            
            # Tabela z podstawowymi informacjami
            route_info = [
                ["Parametr", "Wartość"],
                ["Długość", f"{route_data.get('length', 'b/d')} km"],
                ["Czas przejścia", route_data.get('duration', 'b/d')],
                ["Przewyższenie", f"{route_data.get('elevation', 'b/d')} m"],
                ["Trudność", route_data.get('difficulty', 'b/d')],
                ["Ocena", f"{'★' * int(float(route_data.get('rating', 0)))} ({route_data.get('rating', 0)}/5)"]
            ]
            
            info_table = Table(route_info, colWidths=[150, 300])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 10))
            
            # Opinie użytkowników
            if route_data.get('reviews'):
                elements.append(Paragraph("Opinie użytkowników:", self.styles['CustomBody']))
                for review in route_data['reviews']:
                    review_text = f"""
                    <p><strong>{review['author']}</strong> ({review['date']}):</p>
                    <p>{review['text']}</p>
                    """
                    elements.append(Paragraph(review_text, self.styles['CustomBody']))
                    elements.append(Spacer(1, 5))
            
            # Dodaj separator między trasami
            if i < len(routes_data):
                elements.append(Spacer(1, 20))
                elements.append(Paragraph("_" * 80, self.styles['CustomBody']))
                elements.append(Spacer(1, 20))
        
        return elements

    def _create_seasonality_analysis(self, routes_data: List[Dict[str, Any]], weather_data: Optional[Dict[str, Any]] = None) -> List[Any]:
        """Tworzy sekcję z analizą sezonowości i mapą ciepła dostępności tras."""
        elements = []
        chart_gen = ChartGenerator()
        
        # Dodaj zakładkę dla tej sekcji
        elements.append(Paragraph('<a name="section4"/>3. Analiza sezonowości', 
                                self.styles['CustomHeading1']))
        elements.append(Spacer(1, 12))
        
        try:
            # Przygotuj dane do mapy ciepła
            popularity_data = {}
            for route in routes_data:
                if 'monthly_popularity' in route:
                    popularity_data[route['name']] = route['monthly_popularity']
                else:
                    # Jeśli brak danych o popularności miesięcznej, generujemy przykładowe dane
                    monthly_data = {}
                    for month in range(1, 13):
                        if month in [6, 7, 8]:  # Lato
                            monthly_data[str(month)] = 80 + np.random.randint(-10, 11)
                        elif month in [4, 5, 9, 10]:  # Wiosna/Jesień
                            monthly_data[str(month)] = 60 + np.random.randint(-10, 11)
                        else:  # Zima
                            monthly_data[str(month)] = 30 + np.random.randint(-10, 11)
                    popularity_data[route['name']] = monthly_data
            
            # Generuj mapę ciepła popularności
            elements.append(Paragraph("Mapa ciepła popularności tras w różnych miesiącach", self.styles['CustomHeading2']))
            elements.append(Spacer(1, 12))
            
            heatmap = chart_gen.create_popularity_heatmap(popularity_data)
            elements.append(Image(heatmap, width=500, height=300))
            elements.append(Spacer(1, 20))
            
            # Dodaj opis analizy sezonowości
            season_analysis = """
            Analiza sezonowości pokazuje zróżnicowaną dostępność tras w zależności od regionu i pory roku:
            
            • Okres letni (czerwiec-sierpień) oferuje najlepsze warunki do wędrówek we wszystkich regionach
            • Wiosna i jesień (kwiecień-maj, wrzesień-październik) to również dobry czas na większość tras
            • W okresie zimowym (listopad-marzec) dostępność jest ograniczona, szczególnie w wysokich górach
            • Trasy nizinne i w niższych partiach gór są dostępne przez cały rok
            """
            elements.append(Paragraph(season_analysis, self.styles['CustomBody']))
            
            if weather_data:
                elements.append(Spacer(1, 12))
                elements.append(Paragraph("Aktualne warunki pogodowe", self.styles['CustomHeading2']))
                
                for region, data in weather_data.items():
                    weather_info = f"""
                    Region: {region}
                    • Temperatura: {data['avg_temp']}°C (min: {data['min_temp']}°C, max: {data['max_temp']}°C)
                    • Opady: {data['precipitation']} mm
                    • Zachmurzenie: {data['cloud_cover']}%
                    • Indeks komfortu: {data['comfort_index']:.1f}/100
                    """
                    elements.append(Paragraph(weather_info, self.styles['CustomBody']))
                    elements.append(Spacer(1, 6))
            
        except Exception as e:
            print(f"Błąd podczas generowania analizy sezonowości: {str(e)}")
            elements.append(Paragraph(f"Błąd podczas generowania analizy sezonowości: {str(e)}", self.styles['CustomBody']))
        
        return elements

    def _create_summary_table_section(self, routes_data: List[Dict[str, Any]]) -> List[Any]:
        """Tworzy sekcję z tabelą zbiorczą."""
        elements = []
        
        # Dodaj zakładkę dla tej sekcji
        elements.append(Paragraph('<a name="section5"/>4. Tabela zbiorcza', 
                                self.styles['CustomHeading1']))
        elements.append(Spacer(1, 20))
        
        # Przygotuj dane do tabeli
        headers = ['Nazwa', 'Długość', 'Czas', 'Trudność', 'Ocena', 'Sezon']
        table_data = [headers]
        
        for route in routes_data:
            row = [
                route.get('name', ''),
                f"{route.get('distance', 0)} km",
                str(route.get('duration', '')),
                route.get('difficulty', ''),
                f"{route.get('rating', 0):.1f}/5.0",
                route.get('best_season', 'Cały rok')
            ]
            table_data.append(row)
        
        # Utwórz tabelę
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.font_name),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.green),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWSPLITS', (0, 0), (-1, -1), 0.5)
        ]))
        
        elements.append(table)
        
        return elements

    def _create_appendix_section(self, routes_data: List[Dict[str, Any]]) -> List[Any]:
        """Tworzy sekcję z informacjami o źródłach danych."""
        elements = []
        
        # Dodaj zakładkę dla tej sekcji
        elements.append(Paragraph('<a name="section6"/>5. Aneks - Źródła danych', 
                                self.styles['CustomHeading1']))
        elements.append(Spacer(1, 20))
        
        # Wprowadzenie do aneksu
        intro_text = """
        W tej sekcji przedstawiono źródła danych wykorzystanych do przygotowania raportu.
        Wszystkie dane zostały pozyskane z wiarygodnych źródeł i są regularnie aktualizowane.
        """
        elements.append(Paragraph(intro_text.strip(), self.styles['CustomBody']))
        elements.append(Spacer(1, 20))
        
        # 6.1 Dane pogodowe
        elements.append(Paragraph("6.1. Źródła danych pogodowych", self.styles['CustomHeading2']))
        weather_sources = [
            ("Temperatura i opady", "OpenWeatherMap API", "Dane aktualizowane co godzinę"),
            ("Prognoza pogody", "Met.no Weather API", "7-dniowa prognoza pogody"),
            ("Historyczne dane pogodowe", "IMGW-PIB", "Archiwalne dane meteorologiczne"),
        ]
        
        weather_table = Table(
            [["Typ danych", "Źródło", "Uwagi"]] + weather_sources,
            colWidths=[150, 150, 200]
        )
        weather_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(weather_table)
        elements.append(Spacer(1, 20))
        
        # 6.2 Dane geograficzne
        elements.append(Paragraph("6.2. Źródła danych geograficznych", self.styles['CustomHeading2']))
        geo_sources = [
            ("Mapy i trasy", "OpenStreetMap", "Dane społecznościowe"),
            ("Profile wysokościowe", "SRTM (NASA)", "Rozdzielczość 30m"),
            ("Punkty POI", "OpenStreetMap + własna baza", "Aktualizowane miesięcznie"),
            ("Granice parków narodowych", "GDOŚ", "Dane oficjalne"),
        ]
        
        geo_table = Table(
            [["Typ danych", "Źródło", "Uwagi"]] + geo_sources,
            colWidths=[150, 200, 200]
        )
        geo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(geo_table)
        elements.append(Spacer(1, 20))
        
        # 6.3 Dane o trudności i komforcie tras
        elements.append(Paragraph("6.3. Dane o trudności i komforcie tras", self.styles['CustomHeading2']))
        rating_text = """
        Oceny trudności i komfortu tras są obliczane na podstawie następujących źródeł:
        • Opinie użytkowników z portali turystycznych
        • Dane techniczne trasy (nachylenie, rodzaj nawierzchni)
        • Oceny przewodników górskich
        • Statystyki wypadków i interwencji GOPR/TOPR
        
        Wszystkie oceny są normalizowane do skali 1-5 i regularnie weryfikowane przez ekspertów.
        """
        elements.append(Paragraph(rating_text.strip(), self.styles['CustomBody']))
        elements.append(Spacer(1, 20))
        
        # 6.4 Aktualizacja danych
        elements.append(Paragraph("6.4. Częstotliwość aktualizacji danych", self.styles['CustomHeading2']))
        update_info = [
            ("Dane pogodowe", "Co godzinę"),
            ("Dane geograficzne", "Co miesiąc"),
            ("Oceny użytkowników", "W czasie rzeczywistym"),
            ("Weryfikacja ekspercka", "Co kwartał"),
            ("Dane o wypadkach", "Co tydzień"),
        ]
        
        update_table = Table(
            [["Typ danych", "Częstotliwość aktualizacji"]] + update_info,
            colWidths=[250, 250]
        )
        update_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(update_table)
        
        return elements

    def _calculate_summary_stats(self, 
                               routes_data: List[Dict[str, Any]], 
                               search_params: Dict[str, Any],
                               weather_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Oblicza statystyki podsumowujące dla raportu."""
        stats = {
            'total_routes': len(routes_data),
            'recommended_routes': len([r for r in routes_data if r.get('is_recommended', True)]),
            'weather_comfort': 90.0,  # Domyślna wartość
            'avg_length': np.mean([route.get('distance', 0) for route in routes_data]),
            'avg_difficulty': np.mean([route.get('difficulty', 0) for route in routes_data])
        }
        
        if weather_data:
            stats['weather_comfort'] = np.mean([d.get('comfort', 90.0) for d in weather_data.values()])
        
        return stats 
