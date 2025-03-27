import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
from app.models.vacancy import Vacancy, FunctionCategory, EducationLevel

class AmsterdamScraper:
    BASE_URL = "https://www.amsterdam.nl/werkenbij/"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_vacancies(self) -> List[Dict]:
        try:
            response = self.session.get(self.BASE_URL)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            vacancies = []
            vacancy_elements = soup.find_all('div', class_='vacancy-item')  # Aanpassen aan werkelijke HTML structuur
            
            for element in vacancy_elements:
                vacancy = self._parse_vacancy(element)
                if vacancy:
                    vacancies.append(vacancy)
            
            return vacancies
            
        except Exception as e:
            print(f"Error scraping Amsterdam vacancies: {str(e)}")
            return []
    
    def _parse_vacancy(self, element) -> Optional[Dict]:
        try:
            # Deze methode moet worden aangepast aan de werkelijke HTML structuur
            # van de Amsterdam vacaturepagina
            title = element.find('h2').text.strip()
            url = element.find('a')['href']
            if not url.startswith('http'):
                url = f"https://www.amsterdam.nl{url}"
            
            # Extractie van andere velden moet worden aangepast aan de werkelijke HTML
            description = element.find('div', class_='description').text.strip()
            
            # Voorlopige dummy data voor andere velden
            vacancy_data = {
                'title': title,
                'municipality': 'Amsterdam',
                'url': url,
                'description': description,
                'publication_date': datetime.now(),
                'function_category': FunctionCategory.OTHER,
                'education_level': EducationLevel.HBO,
                'latitude': 52.3676,
                'longitude': 4.9041
            }
            
            return vacancy_data
            
        except Exception as e:
            print(f"Error parsing vacancy: {str(e)}")
            return None

if __name__ == "__main__":
    scraper = AmsterdamScraper()
    vacancies = scraper.get_vacancies()
    print(f"Found {len(vacancies)} vacancies")
    for vacancy in vacancies:
        print(f"- {vacancy['title']}") 