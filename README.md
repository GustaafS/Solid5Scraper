# Nederlandse Gemeentelijke Vacaturetracker

Een geautomatiseerd systeem dat dagelijks de vacaturesites van alle Nederlandse gemeenten controleert op nieuwe vacatures.

## Features

- Dagelijkse scraping van alle Nederlandse gemeentewebsites
- Interactieve kaart-interface voor vacaturevisualisatie
- Geavanceerde zoek- en filterfunctionaliteit
- Gebruikersbeheer met verschillende toegangsniveaus
- Specifieke focus op datafuncties

## Technische Stack

- Backend: Python met FastAPI
- Database: PostgreSQL met PostGIS
- Frontend: React.js met Leaflet/MapboxGL
- Scraping: Python met BeautifulSoup
- Authenticatie: JWT

## Setup

1. Clone de repository
2. Maak een virtuele omgeving aan:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate   # Windows
   ```
3. Installeer dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Maak een `.env` bestand aan met de volgende variabelen:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/vacaturetracker
   SECRET_KEY=your-secret-key
   ```
5. Initialiseer de database:
   ```bash
   alembic upgrade head
   ```
6. Start de development server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Project Structuur

```
├── app/
│   ├── api/           # API endpoints
│   ├── core/          # Core configuratie
│   ├── db/            # Database modellen en migraties
│   ├── models/        # Pydantic modellen
│   ├── schemas/       # Database schemas
│   ├── services/      # Business logic
│   └── utils/         # Utility functies
├── scraper/           # Scraping scripts
├── tests/             # Test bestanden
├── alembic/           # Database migraties
└── frontend/          # React frontend
```

## Licentie

MIT 