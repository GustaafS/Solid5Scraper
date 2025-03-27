"""
Dit bestand bevat alle Nederlandse gemeenten met hun basis informatie.
"""

MUNICIPALITIES = [
    # A
    {"id": 1, "name": "Aa en Hunze", "latitude": 53.0100, "longitude": 6.7500, "website": "https://www.aaenhunze.nl", "vacancy_url": "https://www.werkeninnoordoostoverijssel.nl/vacatures/gemeente-aa-en-hunze"},
    {"id": 2, "name": "Aalsmeer", "latitude": 52.2667, "longitude": 4.7500, "website": "https://www.aalsmeer.nl", "vacancy_url": "https://www.werkenbijaalsmeer.nl/"},
    {"id": 3, "name": "Aalten", "latitude": 51.9167, "longitude": 6.5833, "website": "https://www.aalten.nl", "vacancy_url": "https://www.werkeningelderland.nl/organisatie/gemeente-aalten"},
    {"id": 4, "name": "Achtkarspelen", "latitude": 53.2167, "longitude": 6.1333, "website": "https://www.achtkarspelen.nl", "vacancy_url": "https://www.werkeninfriesland.nl/organisaties/11/gemeente-achtkarspelen"},
    {"id": 5, "name": "Alblasserdam", "latitude": 51.8667, "longitude": 4.6667, "website": "https://www.alblasserdam.nl", "vacancy_url": "https://www.werkenbijdrechtsteden.nl/"},
    {"id": 6, "name": "Albrandswaard", "latitude": 51.8667, "longitude": 4.4000, "website": "https://www.albrandswaard.nl", "vacancy_url": "https://www.werkenvooralbrandswaard.nl/"},
    {"id": 7, "name": "Alkmaar", "latitude": 52.6333, "longitude": 4.7500, "website": "https://www.alkmaar.nl", "vacancy_url": "https://www.werkeninnoordhollandnoord.nl/"},
    {"id": 8, "name": "Almelo", "latitude": 52.3500, "longitude": 6.6667, "website": "https://www.almelo.nl", "vacancy_url": "https://www.werkenintwente.nl/vacatures/gemeente-almelo"},
    {"id": 9, "name": "Almere", "latitude": 52.3667, "longitude": 5.2167, "website": "https://www.almere.nl", "vacancy_url": "https://www.werkenbijalmere.nl/"},
    {"id": 10, "name": "Alphen aan den Rijn", "latitude": 52.1333, "longitude": 4.6667, "website": "https://www.alphenaandenrijn.nl", "vacancy_url": "https://www.werkenbijalphen.nl/"},
    
    # B
    {"id": 11, "name": "Bergen (NH)", "latitude": 52.6667, "longitude": 4.7000, "website": "https://www.bergen-nh.nl", "vacancy_url": "https://www.werkenbijbuch.nl/"},
    {"id": 12, "name": "Bergen op Zoom", "latitude": 51.5000, "longitude": 4.3000, "website": "https://www.bergenopzoom.nl", "vacancy_url": "https://www.werkeninwestbrabant.nl/"},
    {"id": 13, "name": "Berkelland", "latitude": 52.1167, "longitude": 6.5167, "website": "https://www.berkelland.nl", "vacancy_url": "https://www.werkeningelderland.nl/organisatie/gemeente-berkelland"},
    {"id": 14, "name": "Bernheze", "latitude": 51.6833, "longitude": 5.5167, "website": "https://www.bernheze.org", "vacancy_url": "https://www.werkenbijbernheze.nl/"},
    {"id": 15, "name": "Best", "latitude": 51.5167, "longitude": 5.4000, "website": "https://www.gemeentebest.nl", "vacancy_url": "https://www.werkenbijbest.nl/"},
    
    # D
    {"id": 16, "name": "Delft", "latitude": 52.0167, "longitude": 4.3500, "website": "https://www.delft.nl", "vacancy_url": "https://www.werkenvoordelft.nl/"},
    {"id": 17, "name": "Den Haag", "latitude": 52.0833, "longitude": 4.3000, "website": "https://www.denhaag.nl", "vacancy_url": "https://www.werkenbijdenhaag.nl/"},
    {"id": 18, "name": "Den Helder", "latitude": 52.9500, "longitude": 4.7500, "website": "https://www.denhelder.nl", "vacancy_url": "https://www.werkeninnoordhollandnoord.nl/"},
    
    # E
    {"id": 19, "name": "Ede", "latitude": 52.0500, "longitude": 5.6667, "website": "https://www.ede.nl", "vacancy_url": "https://www.werkenbijede.nl/"},
    {"id": 20, "name": "Eindhoven", "latitude": 51.4333, "longitude": 5.4833, "website": "https://www.eindhoven.nl", "vacancy_url": "https://www.werkenvooreindhoven.nl/"},
    
    # G
    {"id": 21, "name": "Groningen", "latitude": 53.2167, "longitude": 6.5667, "website": "https://gemeente.groningen.nl", "vacancy_url": "https://www.werkenbijgemeentegroningen.nl/"},
    
    # H
    {"id": 22, "name": "Haarlem", "latitude": 52.3833, "longitude": 4.6333, "website": "https://www.haarlem.nl", "vacancy_url": "https://www.werkenbijhaarlem.nl/"},
    {"id": 23, "name": "Haarlemmermeer", "latitude": 52.3000, "longitude": 4.7000, "website": "https://www.haarlemmermeer.nl", "vacancy_url": "https://www.werkenbijhaarlemmermeer.nl/"},
    
    # L
    {"id": 24, "name": "Leiden", "latitude": 52.1667, "longitude": 4.4833, "website": "https://www.leiden.nl", "vacancy_url": "https://www.werkenbijleiden.nl/"},
    {"id": 25, "name": "Leeuwarden", "latitude": 53.2000, "longitude": 5.7833, "website": "https://www.leeuwarden.nl", "vacancy_url": "https://www.werkenbijleeuwarden.nl/"},
    
    # M
    {"id": 26, "name": "Maastricht", "latitude": 50.8500, "longitude": 5.6833, "website": "https://www.maastricht.nl", "vacancy_url": "https://www.werkenbijgemeentemaastricht.nl/"},
    
    # N
    {"id": 27, "name": "Nijmegen", "latitude": 51.8333, "longitude": 5.8667, "website": "https://www.nijmegen.nl", "vacancy_url": "https://www.werkenbijnijmegen.nl/"},
    
    # R
    {"id": 28, "name": "Rotterdam", "latitude": 51.9167, "longitude": 4.5000, "website": "https://www.rotterdam.nl", "vacancy_url": "https://www.werkenbijdegemeenterotterdam.nl/"},
    
    # T
    {"id": 29, "name": "Tilburg", "latitude": 51.5500, "longitude": 5.0833, "website": "https://www.tilburg.nl", "vacancy_url": "https://www.werkeninmiddenbrabant.nl/"},
    
    # U
    {"id": 30, "name": "Utrecht", "latitude": 52.0833, "longitude": 5.1167, "website": "https://www.utrecht.nl", "vacancy_url": "https://www.werkenbijutrecht.nl/"},
    
    # Z
    {"id": 31, "name": "Zwolle", "latitude": 52.5167, "longitude": 6.1000, "website": "https://www.zwolle.nl", "vacancy_url": "https://www.werkenbijzwolle.nl/"},
]

def get_all_municipalities():
    """Haal alle gemeenten op"""
    return MUNICIPALITIES

def get_municipality_by_id(id: int):
    """Haal een specifieke gemeente op basis van ID"""
    return next((m for m in MUNICIPALITIES if m["id"] == id), None)

def get_municipality_by_name(name: str):
    """Haal een specifieke gemeente op basis van naam"""
    return next((m for m in MUNICIPALITIES if m["name"].lower() == name.lower()), None) 