import json
from reports.pdf_report_generator import PDFReportGenerator
from data_handlers.route_data_generator import RouteDataGenerator
from typing import Dict, Any, List
import os

def load_routes(file_path: str) -> List[Dict[str, Any]]:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    elif os.path.exists(os.path.join('..', file_path)):
        with open(os.path.join('..', file_path), 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"Nie można znaleźć pliku {file_path}")

def main():
    routes_data = load_routes('rekomendacje.json')
    
    route_generator = RouteDataGenerator()
    routes_data = route_generator.add_elevation_data_to_routes(routes_data)
    
    search_params = {
        'min_length': 0,
        'max_length': 20,
        'region': 'wszystkie',
        'difficulty': 'wszystkie'
    }
    
    pdf_generator = PDFReportGenerator()
    
    try:
        output_file = pdf_generator.generate_route_report(
            routes_data=routes_data,
            search_params=search_params,
            weather_data=None
        )
        print(f"Raport został wygenerowany: {output_file}")
    except Exception as e:
        print(f"Wystąpił błąd podczas generowania raportu: {str(e)}")

if __name__ == "__main__":
    main() 