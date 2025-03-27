# Solid5Scraper

Een applicatie voor het scrapen en visualiseren van gemeentelijke vacatures in Nederland.

## Features

- Scrapen van vacatures van alle Nederlandse gemeentelijke websites
- Interactieve kaart met vacature locaties
- Real-time updates van nieuwe vacatures
- Filtering en zoekfunctionaliteit

## Technische Stack

### Backend
- Python FastAPI
- SQLite database
- BeautifulSoup4 voor web scraping

### Frontend
- React met TypeScript
- Leaflet voor kaartvisualisatie
- Material-UI voor de gebruikersinterface

## Installatie

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm start
```

De applicatie is nu beschikbaar op:
- Frontend: http://localhost:3001
- Backend API: http://localhost:8000

## API Endpoints

- `GET /api/municipalities`: Lijst van alle gemeenten
- `GET /api/vacancies`: Lijst van alle vacatures
- `GET /api/vacancies/{municipality_id}`: Vacatures per gemeente

## Development

Het project is opgedeeld in twee hoofdcomponenten:
1. Een Python backend voor het scrapen en API functionaliteit
2. Een React frontend voor de gebruikersinterface

## Licentie

MIT 