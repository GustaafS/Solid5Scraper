from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from typing import List, Optional, Dict
from pydantic import BaseModel
import httpx
import asyncio
from datetime import datetime, timedelta
import logging
from bs4 import BeautifulSoup
import re
import json
import sqlite3
import os
import sys
import aiosqlite
import csv

# Voeg de parent directory toe aan de Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Logging configuratie
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS configuratie
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Data modellen
class Vacancy(BaseModel):
    id: int
    title: str
    municipality_id: int
    description: str
    function_category: str
    education_level: str
    url: Optional[str] = None
    publication_date: Optional[datetime] = None

class Municipality(BaseModel):
    """Model voor gemeenten"""
    id: str  # Verander naar str voor CBS codes
    name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    website: Optional[str] = None
    vacancy_url: Optional[str] = None
    enabled: bool = True
    last_scraped: Optional[datetime] = None
    success_rate: float = 0
    last_success: Optional[datetime] = None

class ScrapeResult(BaseModel):
    """Model voor scrape resultaten per gemeente"""
    municipality_name: str
    success: bool
    error_message: Optional[str] = None
    urls_found: List[str] = []
    last_scraped: Optional[datetime] = None
    total_vacancies: int = 0

class AdminStats(BaseModel):
    """Model voor admin statistieken"""
    total_municipalities: int
    total_vacancies: int
    last_scrape_time: Optional[datetime] = None
    scrape_results: List[ScrapeResult] = []
    error_count: int = 0
    success_count: int = 0

# Voeg deze variabelen toe bovenaan het bestand, na de andere imports
scraping_progress = {
    "total": 0,
    "current": 0,
    "status": "idle"  # idle, running, completed
}

# Voeg deze functie toe na de andere import functies
async def import_municipalities_from_csv():
    """Importeer alle gemeenten uit het CSV bestand"""
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'municipalities.csv')
    
    try:
        # Maak de data directory als deze nog niet bestaat
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        
        # Open database connectie
        db = await get_db()
        
        # Lees het CSV bestand
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Voeg elke gemeente toe aan de database
                await db.execute('''
                    INSERT OR REPLACE INTO municipalities 
                    (id, name, latitude, longitude, website, vacancy_url, enabled)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                ''', (
                    row['gemeente_code'],
                    row['gemeente_naam'],
                    float(row['latitude']) if row['latitude'] else None,
                    float(row['longitude']) if row['longitude'] else None,
                    f"https://www.{row['gemeente_naam'].lower().replace(' ', '')}.nl",
                    None,  # vacancy_url wordt later handmatig toegevoegd
                ))
        
        await db.commit()
        logger.info("Alle gemeenten succesvol geïmporteerd uit CSV")
        
    except Exception as e:
        logger.error(f"Fout bij importeren gemeenten uit CSV: {e}")
        raise
    finally:
        if 'db' in locals():
            await db.close()

# Update de MUNICIPALITIES lijst met meer gemeenten
MUNICIPALITIES = [
    {
        "id": "GM0363",
        "name": "Amsterdam",
        "latitude": 52.3676,
        "longitude": 4.9041,
        "website": "https://www.amsterdam.nl",
        "vacancy_url": "https://www.amsterdam.nl/werk-en-ondernemen/werken-bij-gemeente/",
        "enabled": True
    },
    {
        "id": "GM0599",
        "name": "Rotterdam",
        "latitude": 51.9225,
        "longitude": 4.4792,
        "website": "https://www.rotterdam.nl",
        "vacancy_url": "https://www.rotterdam.nl/werken-leren/vacatures/",
        "enabled": True
    },
    {
        "id": "GM0518",
        "name": "'s-Gravenhage",  # Den Haag in GeoJSON
        "latitude": 52.0705,
        "longitude": 4.3007,
        "website": "https://www.denhaag.nl",
        "vacancy_url": "https://www.werkenbijdenhaag.nl",
        "enabled": True
    },
    {
        "id": "GM0344",
        "name": "Utrecht",
        "latitude": 52.0907,
        "longitude": 5.1214,
        "website": "https://www.utrecht.nl",
        "vacancy_url": "https://www.utrecht.nl/werk-en-ondernemen/werken-bij-de-gemeente/",
        "enabled": True
    },
    {
        "id": "GM0772",
        "name": "Eindhoven",
        "latitude": 51.4416,
        "longitude": 5.4697,
        "website": "https://www.eindhoven.nl",
        "vacancy_url": "https://www.eindhoven.nl/vacatures",
        "enabled": True
    },
    {
        "id": "GM0014",
        "name": "Groningen",
        "latitude": 53.2194,
        "longitude": 6.5665,
        "website": "https://gemeente.groningen.nl",
        "vacancy_url": "https://gemeente.groningen.nl/vacatures",
        "enabled": True
    },
    {
        "id": "GM0855",
        "name": "Tilburg",
        "latitude": 51.5719,
        "longitude": 5.0672,
        "website": "https://www.tilburg.nl",
        "vacancy_url": "https://www.werkeninmiddenbrabant.nl",
        "enabled": True
    },
    {
        "id": "GM0034",
        "name": "Almere",
        "latitude": 52.3508,
        "longitude": 5.2647,
        "website": "https://www.almere.nl",
        "vacancy_url": "https://www.almere.nl/werken/vacatures",
        "enabled": True
    },
    {
        "id": "GM0758",
        "name": "Breda",
        "latitude": 51.5719,
        "longitude": 4.7683,
        "website": "https://www.breda.nl",
        "vacancy_url": "https://www.werkeninwestbrabant.nl",
        "enabled": True
    },
    {
        "id": "GM0268",
        "name": "Nijmegen",
        "latitude": 51.8425,
        "longitude": 5.8372,
        "website": "https://www.nijmegen.nl",
        "vacancy_url": "https://www.nijmegen.nl/over-de-gemeente/werken-bij-gemeente-nijmegen/",
        "enabled": True
    },
    {
        "id": "GM0153",
        "name": "Enschede",
        "latitude": 52.2215,
        "longitude": 6.8937,
        "website": "https://www.enschede.nl",
        "vacancy_url": "https://www.enschede.nl/werken-bij-de-gemeente",
        "enabled": True
    },
    {
        "id": "GM0141",
        "name": "Almelo",
        "latitude": 52.3570,
        "longitude": 6.6684,
        "website": "https://www.almelo.nl",
        "vacancy_url": "https://www.almelo.nl/werken-bij-de-gemeente",
        "enabled": True
    },
    {
        "id": "GM0307",
        "name": "Amersfoort",
        "latitude": 52.1561,
        "longitude": 5.3878,
        "website": "https://www.amersfoort.nl",
        "vacancy_url": "https://www.amersfoort.nl/werken-bij",
        "enabled": True
    },
    {
        "id": "GM0375",
        "name": "Beverwijk",
        "latitude": 52.4851,
        "longitude": 4.6572,
        "website": "https://www.beverwijk.nl",
        "vacancy_url": "https://www.beverwijk.nl/werken-bij-de-gemeente",
        "enabled": True
    },
    {
        "id": "GM0200",
        "name": "Apeldoorn",
        "latitude": 52.2112,
        "longitude": 5.9699,
        "website": "https://www.apeldoorn.nl",
        "vacancy_url": "https://www.apeldoorn.nl/werken-bij-de-gemeente",
        "enabled": True
    }
]

def get_all_municipalities():
    """Return all municipalities"""
    return MUNICIPALITIES

# Database functies
async def get_db():
    """Get database connection"""
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'scraper.db')
    return await aiosqlite.connect(db_path)

async def init_db():
    """Initialize database tables"""
    try:
        db = await get_db()
        
        # Maak municipalities tabel
        await db.execute('''
        CREATE TABLE IF NOT EXISTS municipalities (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            website TEXT,
            vacancy_url TEXT,
            enabled INTEGER DEFAULT 1,
            last_scraped TIMESTAMP,
            success_rate REAL DEFAULT 0,
            last_success TIMESTAMP
        )
        ''')
        
        # Maak vacancies tabel
        await db.execute('''
        CREATE TABLE IF NOT EXISTS vacancies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            municipality_id TEXT NOT NULL,
            description TEXT,
            function_category TEXT,
            education_level TEXT,
            url TEXT,
            publication_date TIMESTAMP,
            found_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (municipality_id) REFERENCES municipalities (id)
        )
        ''')
        
        # Maak scrape_results tabel
        await db.execute('''
        CREATE TABLE IF NOT EXISTS scrape_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            municipality_name TEXT NOT NULL,
            success INTEGER NOT NULL,
            error_message TEXT,
            urls_found TEXT,
            last_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_vacancies INTEGER DEFAULT 0
        )
        ''')
        
        await db.commit()
        logger.info("Database tabellen succesvol aangemaakt")
        
    except Exception as e:
        logger.error(f"Fout bij initialiseren database: {e}")
        raise
    finally:
        if 'db' in locals():
            await db.close()

# Update de startup_event functie
@app.on_event("startup")
async def startup_event():
    """Initialize database and import municipalities on startup"""
    try:
        # Maak data directory als deze nog niet bestaat
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialiseer de database
        await init_db()
        logger.info("Database geïnitialiseerd")
        
        # Importeer gemeenten uit CSV
        await import_municipalities_from_csv()
        logger.info("Gemeenten geïmporteerd uit CSV")
        
    except Exception as e:
        logger.error(f"Fout bij startup: {e}")
        raise

def load_municipalities():
    """Laad gemeenten uit de database"""
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'scraper.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM municipalities')
    rows = c.fetchall()
    conn.close()
    
    return [Municipality(
        id=row[0],
        name=row[1],
        latitude=float(row[2]) if row[2] is not None else None,
        longitude=float(row[3]) if row[3] is not None else None,
        website=row[4],
        vacancy_url=row[5],
        enabled=bool(row[6]),
        last_scraped=datetime.fromisoformat(row[7]) if row[7] else None,
        success_rate=float(row[8]) if row[8] is not None else 0,
        last_success=datetime.fromisoformat(row[9]) if row[9] else None
    ) for row in rows]

def save_municipality(municipality: Municipality):
    """Sla een gemeente op in de database"""
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'scraper.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO municipalities 
        (id, name, latitude, longitude, website, vacancy_url, enabled, last_scraped)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        municipality.id,
        municipality.name,
        municipality.latitude,
        municipality.longitude,
        municipality.website,
        municipality.vacancy_url,
        municipality.enabled,
        municipality.last_scraped.isoformat() if municipality.last_scraped else None
    ))
    conn.commit()
    conn.close()

def save_vacancy(vacancy: Vacancy):
    """Sla een vacature op in de database"""
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'scraper.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO vacancies 
        (title, municipality_id, description, function_category, education_level, url, publication_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        vacancy.title,
        vacancy.municipality_id,
        vacancy.description,
        vacancy.function_category,
        vacancy.education_level,
        vacancy.url,
        vacancy.publication_date.isoformat() if vacancy.publication_date else None
    ))
    conn.commit()
    conn.close()

async def save_scrape_result(db, municipality_id: int, success: bool, error_message: str = None, urls_found: int = 0):
    """Sla een scrape resultaat op in de database"""
    # Sla het resultaat op
    await db.execute('''
        INSERT INTO scrape_results (municipality_id, success, error_message, urls_found)
        VALUES (?, ?, ?, ?)
    ''', (municipality_id, success, error_message, urls_found))
    
    # Update de gemeente statistieken
    if success:
        await db.execute('''
            UPDATE municipalities 
            SET last_success = CURRENT_TIMESTAMP,
                success_rate = (
                    SELECT CAST(SUM(CASE WHEN success THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100
                    FROM scrape_results
                    WHERE municipality_id = ?
                )
            WHERE id = ?
        ''', (municipality_id, municipality_id))
    
    await db.commit()

# Voeg deze functie toe om de database te vullen met meer gemeenten
async def add_more_municipalities(db):
    """Voeg meer gemeenten toe aan de database"""
    # Hier kunnen we later meer gemeenten toevoegen
    # Voor nu gebruiken we de bestaande lijst
    for municipality in MUNICIPALITIES:
        await db.execute('''
            INSERT OR REPLACE INTO municipalities 
            (id, name, latitude, longitude, website, vacancy_url, enabled)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            municipality["id"],
            municipality["name"],
            municipality["latitude"],
            municipality["longitude"],
            municipality["website"],
            municipality["vacancy_url"],
            municipality["enabled"]
        ))
    await db.commit()

# Globale variabelen voor statistieken
scrape_results: List[ScrapeResult] = []
last_scrape_time: Optional[datetime] = None

# Voeg deze functie toe na de andere load/save functies
def load_vacancies():
    """Laad vacatures uit de database"""
    conn = sqlite3.connect('scraper.db')
    c = conn.cursor()
    c.execute('''SELECT v.*, m.name as municipality_name 
                 FROM vacancies v 
                 JOIN municipalities m ON v.municipality_id = m.id''')
    rows = c.fetchall()
    conn.close()
    
    vacancies = []
    for row in rows:
        vacancies.append({
            "id": row[0],
            "municipality_id": row[1],
            "title": row[2],
            "description": row[3],
            "function_category": row[4],
            "education_level": row[5],
            "url": row[6],
            "publication_date": row[7],
            "found_date": row[8],
            "created_at": row[9],
            "municipality_name": row[10]
        })
    return vacancies

# Scraping functies
async def scrape_municipality(municipality_id: int) -> dict:
    """
    Scrape vacatures voor een specifieke gemeente
    Returns dict met resultaten
    """
    db = None
    try:
        db = await get_db()
        
        # Haal gemeente informatie op
        async with db.execute('SELECT name, website, vacancy_url FROM municipalities WHERE id = ?', (municipality_id,)) as cursor:
            result = await cursor.fetchone()
            if not result:
                return {"success": False, "error": f"Gemeente met ID {municipality_id} niet gevonden"}
            
        name, website, vacancy_url = result
        
        if not vacancy_url:
            error_msg = f"Geen vacancy_url geconfigureerd voor {name}"
            logger.error(error_msg)
            await save_scrape_result(db, municipality_id, False, error_msg)
            return {"success": False, "error": error_msg}
        
        logger.info(f"Start scraping voor {name} ({vacancy_url})")
        
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Probeer eerst de vacancy_url
            try:
                response = await client.get(vacancy_url, headers=headers, timeout=30.0)
                response.raise_for_status()
                current_url = str(response.url)
            except Exception as e:
                logger.warning(f"Kon vacancy_url niet bereiken voor {name}: {str(e)}")
                if website:
                    try:
                        logger.info(f"Probeer algemene website voor {name}: {website}")
                        response = await client.get(website, headers=headers, timeout=30.0)
                        response.raise_for_status()
                        current_url = str(response.url)
                    except Exception as e2:
                        error_msg = f"Kon zowel vacancy_url als website niet bereiken voor {name}: {str(e2)}"
                        logger.error(error_msg)
                        await save_scrape_result(db, municipality_id, False, error_msg)
                        return {"success": False, "error": error_msg}
                else:
                    error_msg = f"Kon vacancy_url niet bereiken en geen alternatieve website voor {name}: {str(e)}"
                    logger.error(error_msg)
                    await save_scrape_result(db, municipality_id, False, error_msg)
                    return {"success": False, "error": error_msg}
            
            # Parse de HTML en zoek vacature links
            soup = BeautifulSoup(response.text, 'html.parser')
            vacancy_links = []
            
            # Zoek naar links die mogelijk naar vacatures verwijzen
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Maak relatieve URLs absoluut
                if href.startswith('/'):
                    href = current_url.rstrip('/') + '/' + href.lstrip('/')
                elif not href.startswith(('http://', 'https://')):
                    href = current_url.rstrip('/') + '/' + href.lstrip('/')
                
                # Check of de link waarschijnlijk naar een vacature verwijst
                if any(keyword in href.lower() for keyword in ['vacature', 'vacancy', 'werken-bij', 'werkenbij', 'jobs', 'careers']):
                    title = link.get_text(strip=True)
                    if not title:
                        title = "Vacature bij " + name
                    
                    logger.info(f"[{name}] Gevonden vacature link: {title} ({href})")
                    vacancy_links.append({
                        'url': href,
                        'title': title
                    })
            
            # Als we geen vacatures vinden, probeer dieper te zoeken
            if not vacancy_links:
                logger.info(f"Geen directe vacature links gevonden voor {name}, zoek in tekst")
                for text in soup.stripped_strings:
                    if any(keyword in text.lower() for keyword in ['vacature', 'vacancy', 'sollicitatie', 'werken bij']):
                        title = text[:100]  # Neem eerste 100 karakters als titel
                        vacancy_links.append({
                            'url': current_url,
                            'title': title
                        })
            
            # Sla gevonden vacatures op
            for vacancy in vacancy_links:
                try:
                    await db.execute('''
                        INSERT OR REPLACE INTO vacancies 
                        (municipality_id, title, url, found_date)
                        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (municipality_id, vacancy['title'], vacancy['url']))
                except Exception as e:
                    logger.error(f"Fout bij opslaan vacature voor {name}: {str(e)}")
            
            # Update gemeente status
            await db.execute('''
                UPDATE municipalities 
                SET last_scraped = CURRENT_TIMESTAMP,
                    last_success = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (municipality_id,))
            
            # Sla scrape resultaat op
            await save_scrape_result(db, municipality_id, True, urls_found=len(vacancy_links))
            await db.commit()
            
            logger.info(f"Scraping voltooid voor {name}: {len(vacancy_links)} vacatures gevonden")
            return {
                "success": True,
                "municipality": name,
                "vacancies_found": len(vacancy_links)
            }
            
    except Exception as e:
        error_msg = f"Onverwachte fout bij scrapen van {name}: {str(e)}"
        logger.error(error_msg)
        if db:
            await save_scrape_result(db, municipality_id, False, error_msg)
        return {"success": False, "error": error_msg}
    
    finally:
        if db:
            try:
                await db.close()
            except Exception as e:
                logger.error(f"Fout bij sluiten database connectie: {str(e)}")

@app.post("/api/scrape")
async def start_scraping(background_tasks: BackgroundTasks):
    """Start het scrapen van alle gemeenten"""
    global scraping_progress
    
    # Reset voortgang
    scraping_progress = {
        "total": 0,
        "current": 0,
        "status": "starting"
    }
    
    try:
        # Start scraping in de achtergrond
        background_tasks.add_task(scrape_all_municipalities)
        return {"message": "Scraping started"}
    except Exception as e:
        logger.error(f"Fout bij starten scraping: {e}")
        scraping_progress["status"] = "error"
        return {"error": str(e)}

async def scrape_all_municipalities():
    """
    Start het scrapen van alle gemeenten
    """
    global scraping_progress
    global last_scrape_time
    
    try:
        # Reset voortgang
        scraping_progress = {
            "total": 0,
            "current": 0,
            "status": "starting"
        }
        
        db = await get_db()
        async with db.execute('SELECT id FROM municipalities WHERE enabled = 1') as cursor:
            rows = await cursor.fetchall()
            municipality_ids = [row[0] for row in rows]
        await db.close()
        
        # Update voortgang
        scraping_progress.update({
            "total": len(municipality_ids),
            "current": 0,
            "status": "running"
        })
        
        logger.info(f"Start scraping voor {len(municipality_ids)} gemeenten")
        
        # Maak batches van 5 gemeenten om tegelijk te scrapen
        batch_size = 5
        results = []
        
        for i in range(0, len(municipality_ids), batch_size):
            batch = municipality_ids[i:i + batch_size]
            batch_tasks = [scrape_municipality(mid) for mid in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Filter en verwerk de resultaten
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Fout tijdens batch scraping: {str(result)}")
                    results.append({"success": False, "error": str(result)})
                else:
                    results.append(result)
            
            # Update voortgang
            scraping_progress["current"] = min(i + batch_size, len(municipality_ids))
            
            # Wacht kort tussen batches om servers niet te overbelasten
            await asyncio.sleep(1)
        
        # Bereken statistieken
        total = len(results)
        successful = sum(1 for r in results if isinstance(r, dict) and r.get('success', False))
        failed = total - successful
        total_vacancies = sum(r.get('vacancies_found', 0) for r in results if isinstance(r, dict) and r.get('success', False))
        
        # Update voortgang naar voltooid
        last_scrape_time = datetime.now()
        scraping_progress = {
            "status": "completed",
            "total": total,
            "current": total,
            "successful_scrapes": successful,
            "failed_scrapes": failed,
            "total_vacancies": total_vacancies,
            "last_scrape": last_scrape_time.isoformat()
        }
        
        logger.info(f"Scraping voltooid: {successful} succesvol, {failed} gefaald, {total_vacancies} vacatures gevonden")
        
    except Exception as e:
        logger.error(f"Fout tijdens scraping: {e}")
        scraping_progress = {
            "status": "error",
            "error": str(e),
            "total": len(municipality_ids) if 'municipality_ids' in locals() else 0,
            "current": scraping_progress.get("current", 0)
        }
        raise

# API endpoints
@app.get("/api/municipalities")
async def get_municipalities():
    """Krijg alle gemeenten"""
    db = await get_db()
    try:
        async with db.execute('SELECT * FROM municipalities') as cursor:
            rows = await cursor.fetchall()
            result = []
            for row in rows:
                result.append({
                    "id": row[0],
                    "name": row[1],
                    "latitude": row[2],
                    "longitude": row[3],
                    "website": row[4],
                    "vacancy_url": row[5],
                    "enabled": row[6],
                    "last_scraped": row[7],
                    "success_rate": row[8],
                    "last_success": row[9]
                })
            return result
    finally:
        await db.close()

@app.get("/api/vacancies")
async def get_vacancies():
    """Krijg alle vacatures"""
    db = await get_db()
    try:
        async with db.execute('''
            SELECT v.*, m.name as municipality_name 
            FROM vacancies v 
            JOIN municipalities m ON v.municipality_id = m.id
            ORDER BY v.found_date DESC
        ''') as cursor:
            rows = await cursor.fetchall()
            
        return [{
            "id": row[0],
            "municipality_id": row[1],
            "title": row[2],
            "description": row[3],
            "function_category": row[4],
            "education_level": row[5],
            "url": row[6],
            "publication_date": row[7],
            "found_date": row[8],
            "created_at": row[9],
            "municipality_name": row[10]
        } for row in rows]
    finally:
        await db.close()

@app.get("/api/stats")
async def get_stats():
    """Krijg statistieken over scraping"""
    db = await get_db()
    try:
        async with db.execute('''
            SELECT 
                COUNT(*) as total_municipalities,
                SUM(CASE WHEN last_scraped IS NOT NULL THEN 1 ELSE 0 END) as scraped_count,
                MAX(last_scraped) as last_scrape_time
            FROM municipalities
        ''') as cursor:
            muni_stats = await cursor.fetchone()
        
        async with db.execute('SELECT COUNT(*) FROM vacancies') as cursor:
            vacancy_count = (await cursor.fetchone())[0]
            
        async with db.execute('''
            SELECT 
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as error_count
            FROM scrape_results
            WHERE scrape_date >= datetime('now', '-1 day')
        ''') as cursor:
            result_stats = await cursor.fetchone()
            
        return {
            "total_municipalities": muni_stats[0],
            "scraped_municipalities": muni_stats[1],
            "last_scrape_time": muni_stats[2],
            "total_vacancies": vacancy_count,
            "success_count": result_stats[0] or 0,
            "error_count": result_stats[1] or 0
        }
    finally:
        await db.close()

@app.get("/api/logs")
async def get_logs():
    """Krijg de laatste scraping logs"""
    db = await get_db()
    try:
        async with db.execute('''
            SELECT 
                sr.municipality_id,
                m.name as municipality_name,
                sr.success,
                sr.error_message,
                sr.urls_found,
                sr.scrape_date
            FROM scrape_results sr
            JOIN municipalities m ON sr.municipality_id = m.id
            ORDER BY sr.scrape_date DESC
            LIMIT 50
        ''') as cursor:
            rows = await cursor.fetchall()
            
        return [{
            "municipality_id": row[0],
            "municipality_name": row[1],
            "success": bool(row[2]),
            "error_message": row[3],
            "urls_found": row[4],
            "scrape_date": row[5]
        } for row in rows]
    finally:
        await db.close()

@app.post("/admin/start-scraping")
async def start_scraping(background_tasks: BackgroundTasks):
    """Start het scrapen van alle gemeenten"""
    try:
        # Start scraping in de achtergrond
        background_tasks.add_task(scrape_all_municipalities)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Admin endpoints
@app.get("/admin", response_class=HTMLResponse)
async def get_admin_dashboard():
    """Admin dashboard pagina"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Solid5 Scraper Admin</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; }
            .card { margin-bottom: 1rem; }
            .log-entry { 
                padding: 0.5rem;
                border-bottom: 1px solid #dee2e6;
                font-family: monospace;
            }
            .log-entry:last-child { border-bottom: none; }
            .success { color: #198754; }
            .error { color: #dc3545; }
            .warning { color: #ffc107; }
            .info { color: #0dcaf0; }
            .progress { margin-top: 1rem; }
        </style>
    </head>
    <body>
        <div class="container mt-4">
            <h1 class="mb-4">Solid5 Scraper Admin</h1>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Scraping Status</h5>
                        </div>
                        <div class="card-body">
                            <div id="stats">
                                <p>Laatste scrape: <span id="last-scrape">-</span></p>
                                <p>Totaal gemeenten: <span id="total-municipalities">-</span></p>
                                <p>Succesvolle scrapes: <span id="successful-scrapes">-</span></p>
                                <p>Mislukte scrapes: <span id="failed-scrapes">-</span></p>
                                <p>Totaal vacatures: <span id="total-vacancies">-</span></p>
                            </div>
                            <div id="progress-container" style="display: none;">
                                <p>Voortgang: <span id="progress-text">0/0</span></p>
                                <div class="progress">
                                    <div id="progress-bar" class="progress-bar" role="progressbar" style="width: 0%"></div>
                                </div>
                            </div>
                            <button class="btn btn-primary mt-3" onclick="startScraping()">Start Scraping</button>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Logs</h5>
                        </div>
                        <div class="card-body" style="max-height: 400px; overflow-y: auto;">
                            <div id="logs"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            async function loadStats() {
                try {
                    const response = await fetch('/api/stats');
                    const data = await response.json();
                    
                    document.getElementById('last-scrape').textContent = 
                        data.last_scrape_time ? new Date(data.last_scrape_time).toLocaleString() : '-';
                    document.getElementById('total-municipalities').textContent = data.total_municipalities;
                    document.getElementById('total-vacancies').textContent = data.total_vacancies;
                    document.getElementById('successful-scrapes').textContent = data.success_count;
                    document.getElementById('failed-scrapes').textContent = data.error_count;
                } catch (error) {
                    console.error('Fout bij ophalen stats:', error);
                }
            }
            
            async function loadProgress() {
                try {
                    const response = await fetch('/api/progress');
                    const data = await response.json();
                    
                    const progressContainer = document.getElementById('progress-container');
                    const progressBar = document.getElementById('progress-bar');
                    const progressText = document.getElementById('progress-text');
                    const button = document.querySelector('button');
                    
                    if (data.status === 'running' || data.status === 'starting') {
                        progressContainer.style.display = 'block';
                        button.disabled = true;
                        button.textContent = 'Bezig met scrapen...';
                        
                        const percentage = (data.current / data.total) * 100;
                        progressBar.style.width = percentage + '%';
                        progressText.textContent = `${data.current}/${data.total} gemeenten`;
                    } else if (data.status === 'completed') {
                        progressContainer.style.display = 'none';
                        button.disabled = false;
                        button.textContent = 'Start Scraping';
                        loadStats(); // Ververs de statistieken
                        loadLogs();  // Ververs de logs
                    } else if (data.status === 'error') {
                        progressContainer.style.display = 'none';
                        button.disabled = false;
                        button.textContent = 'Start Scraping';
                        alert('Fout tijdens scrapen: ' + (data.error || 'Onbekende fout'));
                    } else {
                        progressContainer.style.display = 'none';
                        button.disabled = false;
                        button.textContent = 'Start Scraping';
                    }
                } catch (error) {
                    console.error('Fout bij ophalen voortgang:', error);
                    const button = document.querySelector('button');
                    button.disabled = false;
                    button.textContent = 'Start Scraping';
                }
            }
            
            async function loadLogs() {
                try {
                    const response = await fetch('/api/logs');
                    const logs = await response.json();
                    
                    let html = '';
                    logs.forEach(log => {
                        const className = log.success ? 'success' : 'error';
                        const icon = log.success ? '✅' : '❌';
                        html += `<div class="log-entry ${className}">
                            ${icon} ${log.municipality_name}: ${log.error_message || 'Succesvol'}
                        </div>`;
                    });
                    
                    document.getElementById('logs').innerHTML = html;
                } catch (error) {
                    console.error('Fout bij ophalen logs:', error);
                }
            }
            
            async function startScraping() {
                try {
                    const button = document.querySelector('button');
                    button.disabled = true;
                    button.textContent = 'Bezig met scrapen...';
                    
                    const response = await fetch('/api/scrape', { method: 'POST' });
                    const data = await response.json();
                    
                    if (data.message === 'Scraping started') {
                        document.getElementById('progress-container').style.display = 'block';
                    } else {
                        alert('Fout bij starten scraping: ' + (data.error || 'Onbekende fout'));
                        button.disabled = false;
                        button.textContent = 'Start Scraping';
                    }
                } catch (error) {
                    console.error('Fout bij starten scraping:', error);
                    alert('Fout bij starten scraping');
                    const button = document.querySelector('button');
                    button.disabled = false;
                    button.textContent = 'Start Scraping';
                }
            }
            
            // Laad initiële data
            loadStats();
            loadLogs();
            loadProgress();
            
            // Update elke 2 seconden
            setInterval(() => {
                loadStats();
                loadLogs();
                loadProgress();
            }, 2000);
        </script>
    </body>
    </html>
    """

@app.get("/admin/municipalities", response_model=List[Municipality])
async def get_municipalities_config():
    """Krijg de configuratie van alle gemeenten"""
    db = await get_db()
    try:
        async with db.execute('SELECT * FROM municipalities') as cursor:
            rows = await cursor.fetchall()
            result = []
            for row in rows:
                result.append({
                    "id": row[0],
                    "name": row[1],
                    "latitude": row[2],
                    "longitude": row[3],
                    "website": row[4],
                    "vacancy_url": row[5],
                    "enabled": bool(row[6]),
                    "last_scraped": row[7],
                    "success_rate": row[8],
                    "last_success": row[9]
                })
            return result
    finally:
        await db.close()

@app.put("/admin/municipalities/{municipality_id}")
async def update_municipality_config(municipality_id: int, config: Municipality):
    """Update de configuratie van een gemeente"""
    db = await get_db()
    try:
        await db.execute('''
            UPDATE municipalities 
            SET name = ?, latitude = ?, longitude = ?, website = ?, vacancy_url = ?, enabled = ?
            WHERE id = ?
        ''', (
            config.name,
            config.latitude,
            config.longitude,
            config.website,
            config.vacancy_url,
            config.enabled,
            municipality_id
        ))
        await db.commit()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Fout bij updaten gemeente: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await db.close()

# Voeg deze nieuwe endpoint toe voor de voortgang
@app.get("/api/progress")
async def get_progress():
    """Haal de huidige scraping voortgang op"""
    return scraping_progress 