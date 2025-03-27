from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.vacancy import Vacancy
from app.schemas.vacancy import VacancyCreate, VacancyUpdate

def get_vacancy(db: Session, vacancy_id: int) -> Optional[Vacancy]:
    return db.query(Vacancy).filter(Vacancy.id == vacancy_id).first()

def get_vacancies(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    municipality: Optional[str] = None,
    function_category: Optional[str] = None,
    education_level: Optional[str] = None
) -> List[Vacancy]:
    query = db.query(Vacancy)
    
    if municipality:
        query = query.filter(Vacancy.municipality == municipality)
    if function_category:
        query = query.filter(Vacancy.function_category == function_category)
    if education_level:
        query = query.filter(Vacancy.education_level == education_level)
    
    return query.offset(skip).limit(limit).all()

def create_vacancy(db: Session, vacancy: VacancyCreate) -> Vacancy:
    db_vacancy = Vacancy(**vacancy.model_dump())
    db.add(db_vacancy)
    db.commit()
    db.refresh(db_vacancy)
    return db_vacancy

def update_vacancy(
    db: Session,
    vacancy_id: int,
    vacancy: VacancyUpdate
) -> Optional[Vacancy]:
    db_vacancy = get_vacancy(db, vacancy_id)
    if not db_vacancy:
        return None
    
    for field, value in vacancy.model_dump(exclude_unset=True).items():
        setattr(db_vacancy, field, value)
    
    db.commit()
    db.refresh(db_vacancy)
    return db_vacancy

def delete_vacancy(db: Session, vacancy_id: int) -> bool:
    db_vacancy = get_vacancy(db, vacancy_id)
    if not db_vacancy:
        return False
    
    db.delete(db_vacancy)
    db.commit()
    return True

def get_vacancies_by_municipality(db: Session, municipality_id: int) -> List[Vacancy]:
    return db.query(Vacancy).filter(Vacancy.municipality_id == municipality_id).all()

def get_data_vacancies(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Vacancy]:
    return db.query(Vacancy).filter(
        Vacancy.function_category == "DATA"
    ).offset(skip).limit(limit).all() 