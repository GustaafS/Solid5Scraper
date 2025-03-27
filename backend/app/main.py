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

# Voeg de parent directory toe aan de Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import municipalities  # Import vanuit de app package

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
    id: int
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

# Database setup
def init_db():
    """Initialiseer de database met alle gemeenten"""
    try:
        db_path = os.path.join(os.path.dirname(__file__), '..', 'scraper.db')
        logger.info(f"Database pad: {db_path}")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Maak tabellen aan
        c.execute('''CREATE TABLE IF NOT EXISTS municipalities
                     (id INTEGER PRIMARY KEY,
                      name TEXT NOT NULL,
                      latitude REAL,
                      longitude REAL,
                      website TEXT,
                      vacancy_url TEXT,
                      enabled BOOLEAN DEFAULT TRUE,
                      last_scraped TIMESTAMP,
                      success_rate REAL DEFAULT 0,
                      last_success TIMESTAMP)''')
                  
        c.execute('''CREATE TABLE IF NOT EXISTS vacancies
                     (id INTEGER PRIMARY KEY,
                      municipality_id INTEGER,
                      title TEXT NOT NULL,
                      description TEXT,
                      url TEXT NOT NULL,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (municipality_id) REFERENCES municipalities (id))''')
                  
        c.execute('''CREATE TABLE IF NOT EXISTS scrape_results
                     (id INTEGER PRIMARY KEY,
                      municipality_id INTEGER,
                      success BOOLEAN,
                      error_message TEXT,
                      scrape_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY (municipality_id) REFERENCES municipalities (id))''')

        # Controleer of er al gemeenten in de database zitten
        c.execute('SELECT COUNT(*) FROM municipalities')
        count = c.fetchone()[0]
        
        if count == 0:
            logging.info("Database is leeg, voeg alle gemeenten toe...")
            # Voeg alle gemeenten toe uit de municipalities module
            for m in municipalities.get_all_municipalities():
                # Log de gemeente data voor debugging
                logging.info(f"Toevoegen gemeente: {m['name']} met coördinaten: {m.get('latitude')}, {m.get('longitude')}")
                
                c.execute('''INSERT INTO municipalities 
                           (id, name, latitude, longitude, website, vacancy_url, enabled)
                           VALUES (?, ?, ?, ?, ?, ?, 1)''',
                         (m["id"], m["name"], m.get("latitude"), m.get("longitude"), m["website"], m["vacancy_url"]))
            logging.info(f"{len(municipalities.get_all_municipalities())} gemeenten toegevoegd aan database")
        
        # Verwijder bestaande gemeenten en voeg ze opnieuw toe
        else:
            logging.info("Database bevat al gemeenten, opnieuw toevoegen...")
            c.execute('DELETE FROM municipalities')
            for m in municipalities.get_all_municipalities():
                logging.info(f"Toevoegen gemeente: {m['name']} met coördinaten: {m.get('latitude')}, {m.get('longitude')}")
                c.execute('''INSERT INTO municipalities 
                           (id, name, latitude, longitude, website, vacancy_url, enabled)
                           VALUES (?, ?, ?, ?, ?, ?, 1)''',
                         (m["id"], m["name"], m.get("latitude"), m.get("longitude"), m["website"], m["vacancy_url"]))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Fout bij initialiseren van de database: {str(e)}")

def load_municipalities():
    """Laad gemeenten uit de database"""
    conn = sqlite3.connect('scraper.db')
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
    conn = sqlite3.connect('scraper.db')
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
    conn = sqlite3.connect('scraper.db')
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

def save_scrape_result(municipality_id: int, success: bool, error_message: str = None, urls_found: int = 0):
    """Sla een scrape resultaat op in de database"""
    conn = sqlite3.connect('scraper.db')
    c = conn.cursor()
    
    # Sla het resultaat op
    c.execute('''
        INSERT INTO scrape_results (municipality_id, success, error_message, urls_found)
        VALUES (?, ?, ?, ?)
    ''', (municipality_id, success, error_message, urls_found))
    
    # Update de gemeente statistieken
    if success:
        c.execute('''
            UPDATE municipalities 
            SET last_success = CURRENT_TIMESTAMP,
                success_rate = (
                    SELECT CAST(SUM(CASE WHEN success THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100
                    FROM scrape_results
                    WHERE municipality_id = ?
                )
            WHERE id = ?
        ''', (municipality_id, municipality_id))
    
    conn.commit()
    conn.close()

# Voeg een functie toe om gemeenten in batches toe te voegen
def add_more_municipalities():
    """Voeg meer gemeenten toe aan de database"""
    conn = sqlite3.connect('scraper.db')
    c = conn.cursor()
    
    # Haal het laatste gemeente ID op
    c.execute('SELECT MAX(id) FROM municipalities')
    last_id = c.fetchone()[0] or 0
    
    # Voeg de volgende batch gemeenten toe
    municipalities = [
        (last_id + 1, "Baarle-Nassau", 51.4500, 4.9333, "https://www.baarle-nassau.nl", "https://www.baarle-nassau.nl/werken-bij", 1, None, 0, None),
        (last_id + 2, "Baarn", 52.2117, 5.2883, "https://www.baarn.nl", "https://www.baarn.nl/werken-bij", 1, None, 0, None),
        (last_id + 3, "Barneveld", 52.1333, 5.5833, "https://www.barneveld.nl", "https://www.barneveld.nl/werken-bij", 1, None, 0, None),
        # Voeg hier meer gemeenten toe...
    ]
    
    c.executemany('''
        INSERT INTO municipalities 
        (id, name, latitude, longitude, website, vacancy_url, enabled, last_scraped, success_rate, last_success)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', municipalities)
    
    conn.commit()
    conn.close()
    
    logger.info(f"Extra {len(municipalities)} gemeenten toegevoegd aan de database")

# Initialiseer de database bij startup
init_db()

# Database simulatie (later kunnen we dit vervangen door een echte database)
municipalities = load_municipalities()
vacancies = []  # Deze lijst wordt gevuld door de scraper

# Globale variabelen voor statistieken
scrape_results: List[ScrapeResult] = []
last_scrape_time: Optional[datetime] = None

# Scraping functies
async def scrape_municipality(municipality_id: int) -> dict:
    """
    Scrape vacatures voor een specifieke gemeente
    Returns dict met resultaten
    """
    conn = sqlite3.connect('scraper.db')
    c = conn.cursor()
    
    # Haal gemeente informatie op
    c.execute('SELECT name, website, vacancy_url FROM municipalities WHERE id = ?', (municipality_id,))
    result = c.fetchone()
    if not result:
        return {"success": False, "error": f"Gemeente met ID {municipality_id} niet gevonden"}
        
    name, website, vacancy_url = result
    
    if not vacancy_url:
        error_msg = f"Geen vacancy_url geconfigureerd voor {name}"
        c.execute('''INSERT INTO scrape_results 
                     (municipality_id, success, error_message, scrape_date)
                     VALUES (?, 0, ?, CURRENT_TIMESTAMP)''',
                 (municipality_id, error_msg))
        conn.commit()
        return {"success": False, "error": error_msg}
    
    logger.info(f"Start scraping voor {name} ({vacancy_url})")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(vacancy_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Zoek naar links die mogelijk naar vacatures verwijzen
            vacancy_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Maak relatieve URLs absoluut
                if href.startswith('/'):
                    href = website + href
                    
                # Check of de link waarschijnlijk naar een vacature verwijst
                if any(keyword in href.lower() for keyword in ['vacature', 'vacancies', 'werken', 'jobs']):
                    vacancy_links.append({
                        'url': href,
                        'title': link.get_text(strip=True) or href
                    })
            
            # Sla gevonden vacatures op
            for i, vacancy in enumerate(vacancy_links, 1):
                logger.info(f"[{name}] Vacature {i}/{len(vacancy_links)}: {vacancy['title']}")
                c.execute('''INSERT OR IGNORE INTO vacancies 
                           (municipality_id, title, url, found_date)
                           VALUES (?, ?, ?, CURRENT_TIMESTAMP)''',
                        (municipality_id, vacancy['title'], vacancy['url']))
            
            # Update gemeente statistieken
            c.execute('''UPDATE municipalities 
                        SET last_scraped = CURRENT_TIMESTAMP,
                            success_rate = (success_rate + 1.0) / 2
                        WHERE id = ?''', (municipality_id,))
            
            # Log succesvol resultaat
            c.execute('''INSERT INTO scrape_results 
                        (municipality_id, success, scrape_date)
                        VALUES (?, 1, CURRENT_TIMESTAMP)''',
                     (municipality_id,))
            
            conn.commit()
            return {
                "success": True,
                "municipality": name,
                "vacancies_found": len(vacancy_links)
            }
            
    except Exception as e:
        error_msg = f"Fout bij scrapen van {name}: {str(e)}"
        logger.error(error_msg)
        
        # Log fout resultaat
        c.execute('''INSERT INTO scrape_results 
                     (municipality_id, success, error_message, scrape_date)
                     VALUES (?, 0, ?, CURRENT_TIMESTAMP)''',
                 (municipality_id, error_msg))
        
        # Update gemeente statistieken
        c.execute('''UPDATE municipalities 
                    SET last_scraped = CURRENT_TIMESTAMP,
                        success_rate = success_rate / 2
                    WHERE id = ?''', (municipality_id,))
        
        conn.commit()
        return {"success": False, "error": error_msg}
    
    finally:
        conn.close()

async def scrape_all_municipalities():
    """
    Start het scrapen van alle gemeenten
    """
    conn = sqlite3.connect('scraper.db')
    c = conn.cursor()
    
    # Haal alle actieve gemeenten op
    c.execute('SELECT id FROM municipalities WHERE enabled = 1')
    municipality_ids = [row[0] for row in c.fetchall()]
    conn.close()
    
    logger.info(f"Start scraping voor {len(municipality_ids)} gemeenten")
    
    # Maak batches van 5 gemeenten om tegelijk te scrapen
    batch_size = 5
    results = []
    
    for i in range(0, len(municipality_ids), batch_size):
        batch = municipality_ids[i:i + batch_size]
        batch_tasks = [scrape_municipality(mid) for mid in batch]
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        results.extend(batch_results)
        
        # Wacht kort tussen batches om servers niet te overbelasten
        await asyncio.sleep(1)
    
    # Bereken statistieken
    total = len(results)
    successful = sum(1 for r in results if isinstance(r, dict) and r.get('success', False))
    failed = total - successful
    total_vacancies = sum(r.get('vacancies_found', 0) for r in results if isinstance(r, dict) and r.get('success', False))
    
    logger.info(f"Scraping voltooid: {successful} succesvol, {failed} gefaald, {total_vacancies} vacatures gevonden")
    
    return {
        "total_municipalities": total,
        "successful_scrapes": successful,
        "failed_scrapes": failed,
        "total_vacancies": total_vacancies
    }

# API endpoints
@app.get("/api/municipalities")
async def get_municipalities():
    conn = sqlite3.connect('scraper.db')
    c = conn.cursor()
    c.execute('SELECT * FROM municipalities')
    municipalities = []
    for row in c.fetchall():
        municipalities.append({
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
    conn.close()
    return municipalities

@app.get("/api/vacancies")
async def get_vacancies():
    conn = sqlite3.connect('scraper.db')
    c = conn.cursor()
    c.execute('''SELECT v.*, m.name as municipality_name 
                 FROM vacancies v 
                 JOIN municipalities m ON v.municipality_id = m.id''')
    vacancies = []
    for row in c.fetchall():
        vacancies.append({
            "id": row[0],
            "municipality_id": row[1],
            "title": row[2],
            "description": row[3],
            "url": row[4],
            "created_at": row[5],
            "municipality_name": row[6]
        })
    conn.close()
    return vacancies

@app.get("/api/stats")
async def get_stats():
    conn = sqlite3.connect('scraper.db')
    c = conn.cursor()
    
    # Get total municipalities
    c.execute('SELECT COUNT(*) FROM municipalities')
    total_municipalities = c.fetchone()[0]
    
    # Get enabled municipalities
    c.execute('SELECT COUNT(*) FROM municipalities WHERE enabled = 1')
    enabled_municipalities = c.fetchone()[0]
    
    # Get total vacancies
    c.execute('SELECT COUNT(*) FROM vacancies')
    total_vacancies = c.fetchone()[0]
    
    # Get last scrape time
    c.execute('SELECT MAX(scrape_date) FROM scrape_results')
    last_scrape = c.fetchone()[0]
    
    # Get success rate
    c.execute('''SELECT COUNT(*) FROM scrape_results WHERE success = 1''')
    successful_scrapes = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM scrape_results')
    total_scrapes = c.fetchone()[0]
    success_rate = (successful_scrapes / total_scrapes * 100) if total_scrapes > 0 else 0
    
    conn.close()
    
    return {
        "total_municipalities": total_municipalities,
        "enabled_municipalities": enabled_municipalities,
        "total_vacancies": total_vacancies,
        "last_scrape": last_scrape,
        "success_rate": round(success_rate, 2)
    }

@app.get("/api/logs")
async def get_logs():
    conn = sqlite3.connect('scraper.db')
    c = conn.cursor()
    c.execute('''SELECT sr.*, m.name as municipality_name 
                 FROM scrape_results sr 
                 JOIN municipalities m ON sr.municipality_id = m.id 
                 ORDER BY sr.scrape_date DESC 
                 LIMIT 100''')
    logs = []
    for row in c.fetchall():
        logs.append({
            "id": row[0],
            "municipality_id": row[1],
            "success": bool(row[2]),
            "error_message": row[3],
            "scrape_date": row[4],
            "municipality_name": row[5]
        })
    conn.close()
    return logs

@app.post("/api/scrape")
async def start_scraping(background_tasks: BackgroundTasks):
    background_tasks.add_task(scrape_all_municipalities)
    return {"message": "Scraping started"}

@app.post("/admin/start-scraping")
async def start_scraping(background_tasks: BackgroundTasks):
    """Start het scrapen van alle gemeenten"""
    try:
        # Start scraping in de achtergrond
        background_tasks.add_task(scrape_all_municipalities)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Start initiële scraping bij opstarten
@app.on_event("startup")
async def startup_event():
    await scrape_all_municipalities()

# Admin endpoints
@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    """Admin pagina voor het beheren van de scraper"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vacature Scraper Admin</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { padding: 20px; }
            .card { margin-bottom: 20px; }
            #logs { height: 400px; overflow-y: auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Vacature Scraper Admin</h1>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Scraping Status</h5>
                        </div>
                        <div class="card-body">
                            <div id="stats">Laden...</div>
                            <button onclick="startScraping()" class="btn btn-primary mt-3">Start Scraping</button>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">Logs</h5>
                        </div>
                        <div class="card-body">
                            <pre id="logs">Laden...</pre>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Functie om statistieken op te halen
            async function loadStats() {
                try {
                    const response = await fetch('/admin/stats');
                    const data = await response.json();
                    
                    let html = `
                        <table class="table">
                            <tr><td>Laatste scrape:</td><td>${data.last_scrape || 'Nooit'}</td></tr>
                            <tr><td>Totaal gemeenten:</td><td>${data.total_municipalities}</td></tr>
                            <tr><td>Succesvol:</td><td>${data.successful_scrapes}</td></tr>
                            <tr><td>Gefaald:</td><td>${data.failed_scrapes}</td></tr>
                            <tr><td>Totaal vacatures:</td><td>${data.total_vacancies}</td></tr>
                        </table>
                    `;
                    
                    document.getElementById('stats').innerHTML = html;
                } catch (error) {
                    console.error('Fout bij ophalen stats:', error);
                }
            }
            
            // Functie om logs op te halen
            async function loadLogs() {
                try {
                    const response = await fetch('/admin/logs');
                    const data = await response.text();
                    document.getElementById('logs').textContent = data;
                    
                    // Scroll naar beneden
                    const logsDiv = document.getElementById('logs');
                    logsDiv.scrollTop = logsDiv.scrollHeight;
                } catch (error) {
                    console.error('Fout bij ophalen logs:', error);
                }
            }
            
            // Functie om scraping te starten
            async function startScraping() {
                try {
                    const button = document.querySelector('button');
                    button.disabled = true;
                    button.textContent = 'Bezig met scrapen...';
                    
                    const response = await fetch('/admin/start-scraping', { method: 'POST' });
                    const data = await response.json();
                    
                    if (data.success) {
                        alert('Scraping gestart!');
                    } else {
                        alert('Fout bij starten scraping: ' + data.error);
                    }
                } catch (error) {
                    console.error('Fout bij starten scraping:', error);
                    alert('Fout bij starten scraping');
                } finally {
                    button.disabled = false;
                    button.textContent = 'Start Scraping';
                }
            }
            
            // Ververs elke 30 seconden
            setInterval(() => {
                loadStats();
                loadLogs();
            }, 30000);
            
            // Laad direct bij opstarten
            loadStats();
            loadLogs();
        </script>
    </body>
    </html>
    """

@app.get("/admin/stats")
def get_admin_stats():
    """Haal statistieken op voor de admin interface"""
    conn = sqlite3.connect('scraper.db')
    c = conn.cursor()
    
    # Haal laatste scrape tijd op
    c.execute('''SELECT MAX(scrape_date) FROM scrape_results''')
    last_scrape = c.fetchone()[0]
    
    # Tel totaal aantal gemeenten
    c.execute('''SELECT COUNT(*) FROM municipalities''')
    total_municipalities = c.fetchone()[0]
    
    # Tel succesvolle en gefaalde scrapes van laatste ronde
    c.execute('''SELECT 
                    COUNT(*) FILTER (WHERE success = 1) as successful,
                    COUNT(*) FILTER (WHERE success = 0) as failed
                 FROM scrape_results 
                 WHERE scrape_date = (SELECT MAX(scrape_date) FROM scrape_results)''')
    successful_scrapes, failed_scrapes = c.fetchone()
    
    # Tel totaal aantal vacatures
    c.execute('''SELECT COUNT(*) FROM vacancies''')
    total_vacancies = c.fetchone()[0]
    
    conn.close()
    
    return {
        "last_scrape": last_scrape,
        "total_municipalities": total_municipalities,
        "successful_scrapes": successful_scrapes or 0,
        "failed_scrapes": failed_scrapes or 0,
        "total_vacancies": total_vacancies
    }

@app.get("/admin/logs")
def get_admin_logs():
    """Haal de laatste 100 log regels op"""
    conn = sqlite3.connect('scraper.db')
    c = conn.cursor()
    
    # Haal de laatste 100 scrape resultaten op
    c.execute('''SELECT 
                    m.name,
                    s.success,
                    s.error_message,
                    s.scrape_date
                 FROM scrape_results s
                 JOIN municipalities m ON m.id = s.municipality_id
                 ORDER BY s.scrape_date DESC
                 LIMIT 100''')
    
    results = c.fetchall()
    conn.close()
    
    # Formatteer de resultaten als log regels
    log_lines = []
    for name, success, error, date in results:
        if success:
            log_lines.append(f"[{date}] ✅ {name}: Succesvol")
        else:
            log_lines.append(f"[{date}] ❌ {name}: {error}")
    
    return "\n".join(log_lines)

@app.get("/admin/municipalities", response_model=List[Municipality])
async def get_municipalities_config():
    """Krijg de configuratie van alle gemeenten"""
    return municipalities

@app.put("/admin/municipalities/{municipality_id}")
async def update_municipality_config(municipality_id: int, config: Municipality):
    """Update de configuratie van een gemeente"""
    global municipalities
    for i, m in enumerate(municipalities):
        if m.id == municipality_id:
            municipalities[i] = config
            save_municipality(municipality)
            return {"status": "success"}
    raise HTTPException(status_code=404, detail="Gemeente niet gevonden")

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
                const response = await fetch('/admin/stats');
                const data = await response.json();
                
                document.getElementById('last-scrape').textContent = 
                    data.last_scrape_time ? new Date(data.last_scrape_time).toLocaleString() : '-';
                document.getElementById('total-municipalities').textContent = data.total_municipalities;
                document.getElementById('total-vacancies').textContent = data.total_vacancies;
                
                const successful = data.scrape_results.filter(r => r.success).length;
                const failed = data.scrape_results.filter(r => !r.success).length;
                
                document.getElementById('successful-scrapes').textContent = successful;
                document.getElementById('failed-scrapes').textContent = failed;
            }
            
            async function loadLogs() {
                const response = await fetch('/admin/logs');
                const logs = await response.text();
                document.getElementById('logs').innerHTML = logs;
            }
            
            async function startScraping() {
                await fetch('/scrape', { method: 'POST' });
                loadStats();
                loadLogs();
            }
            
            // Laad initiële data
            loadStats();
            loadLogs();
            
            // Update elke 30 seconden
            setInterval(() => {
                loadStats();
                loadLogs();
            }, 30000);
        </script>
    </body>
    </html>
    """ 