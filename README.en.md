# Tourist route recommender

[Polski](README.md) | **English**

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![ReportLab](https://img.shields.io/badge/ReportLab-PDF-c0392b)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-HTML%20parsing-4B8BBE)
![pytest](https://img.shields.io/badge/pytest-10%20tests-0A9EDC?logo=pytest&logoColor=white)

A console application that suggests hiking routes for a chosen day. You pick a temperature range, route length and difficulty, and a region. The program compares them with the weather forecast, scores every route and writes a PDF report with charts.

## How it works

1. Loads routes from `data/trasy/trasy.csv` (15 routes in 10 regions) and weather data from `data/pogoda/pogoda.csv`.
2. Drops routes outside the length and difficulty limits.
3. For each remaining route, computes how well the weather in its region fits (temperature, rainfall, cloud cover) and how well the route itself fits (difficulty and length), then combines the two with weights.
4. Saves a PDF report to the `raporty/` folder.

```mermaid
flowchart LR
    U[/"preferences: temperature, length, difficulty, region"/] --> F
    T[("trasy.csv<br/>15 routes, 10 regions")] --> F["filter: length and difficulty"]
    W[("pogoda.csv")] --> S
    F --> S["score: route fit + weather fit"]
    H[("route_reviews/*.html")] --> R["review analysis: TextBlob"]
    R --> P
    S --> P[["PDF report: ReportLab"]]
```

All data comes from files in the repository, so the program does not need internet access.

## PDF report

- elevation profiles of the routes,
- comparison charts (length, difficulty, categories),
- a heatmap of availability across the year,
- a summary table,
- an appendix with data sources and the scoring method.

The report uses the DejaVu Sans font, so Polish characters render correctly on any system.

## Running

Requires Python 3.9 or newer.

```bash
git clone https://github.com/MataKomandos/System-rekomendacji-tras-turystycznych.git
cd System-rekomendacji-tras-turystycznych

python -m venv venv
venv\Scripts\activate            # Linux/macOS: source venv/bin/activate

pip install -r requirements.txt
python main.py
```

The program asks for your preferences (in Polish): minimum and maximum temperature, route length, difficulty (1-5) and region. The report goes to `raporty/`.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The tests cover the weather comfort index, rejecting days with too much rainfall, filtering routes by limits, sorting results, skipping regions without weather data, and the average rating from reviews.

## Structure

```
main.py                     entry point
data/
├── trasy/trasy.csv         route descriptions
├── pogoda/pogoda.csv       weather data
└── route_reviews/          route reviews (HTML)
src/
├── models/                 Trasa, DanePogodowe, PreferencjeUzytkownika
├── recommenders/           route scoring and sorting
├── analyzers/              weather and review analysis
├── data_handlers/          data loading, route ratings
├── interface/              console handling
└── reports/                charts and PDF generator
tests/                      pytest tests
raporty/                    generated reports (not in git)
```
