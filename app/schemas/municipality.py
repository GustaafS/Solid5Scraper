from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, List
from app.schemas.vacancy import Vacancy

class MunicipalityBase(BaseModel):
    name: str
    website: Optional[HttpUrl] = None
    vacancy_page_url: Optional[HttpUrl] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_active: bool = True

class MunicipalityCreate(MunicipalityBase):
    pass

class MunicipalityUpdate(MunicipalityBase):
    pass

class MunicipalityInDBBase(MunicipalityBase):
    id: int
    last_scraped: Optional[datetime] = None

    class Config:
        from_attributes = True

class Municipality(MunicipalityInDBBase):
    vacancies: List[Vacancy] = []

class MunicipalityInDB(MunicipalityInDBBase):
    pass 