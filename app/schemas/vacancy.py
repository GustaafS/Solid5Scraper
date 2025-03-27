from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional
from app.models.vacancy import FunctionCategory, EducationLevel

class VacancyBase(BaseModel):
    title: str
    municipality: str
    salary_scale: Optional[str] = None
    education_level: Optional[EducationLevel] = None
    function_category: Optional[FunctionCategory] = None
    description: Optional[str] = None
    url: HttpUrl
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    data_tools: Optional[str] = None
    data_experience_years: Optional[int] = None
    data_certifications: Optional[str] = None

class VacancyCreate(VacancyBase):
    municipality_id: int
    publication_date: datetime
    closing_date: Optional[datetime] = None

class VacancyUpdate(VacancyBase):
    pass

class VacancyInDBBase(VacancyBase):
    id: int
    municipality_id: int
    publication_date: datetime
    closing_date: Optional[datetime] = None

    class Config:
        from_attributes = True

class Vacancy(VacancyInDBBase):
    pass

class VacancyInDB(VacancyInDBBase):
    pass 