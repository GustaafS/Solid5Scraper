from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import crud
from app.api import deps
from app.schemas.vacancy import Vacancy, VacancyCreate, VacancyUpdate
from app.models.vacancy import FunctionCategory, EducationLevel

router = APIRouter()

@router.get("/", response_model=List[Vacancy])
def read_vacancies(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    municipality: Optional[str] = None,
    function_category: Optional[FunctionCategory] = None,
    education_level: Optional[EducationLevel] = None
):
    """
    Haal alle vacatures op met optionele filters.
    """
    vacancies = crud.vacancy.get_vacancies(
        db,
        skip=skip,
        limit=limit,
        municipality=municipality,
        function_category=function_category,
        education_level=education_level
    )
    return vacancies

@router.post("/", response_model=Vacancy)
def create_vacancy(
    *,
    db: Session = Depends(deps.get_db),
    vacancy_in: VacancyCreate
):
    """
    Maak een nieuwe vacature aan.
    """
    vacancy = crud.vacancy.create_vacancy(db=db, vacancy=vacancy_in)
    return vacancy

@router.get("/{vacancy_id}", response_model=Vacancy)
def read_vacancy(
    vacancy_id: int,
    db: Session = Depends(deps.get_db)
):
    """
    Haal een specifieke vacature op door ID.
    """
    vacancy = crud.vacancy.get_vacancy(db=db, vacancy_id=vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacature niet gevonden")
    return vacancy

@router.put("/{vacancy_id}", response_model=Vacancy)
def update_vacancy(
    *,
    db: Session = Depends(deps.get_db),
    vacancy_id: int,
    vacancy_in: VacancyUpdate
):
    """
    Update een vacature.
    """
    vacancy = crud.vacancy.get_vacancy(db=db, vacancy_id=vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacature niet gevonden")
    vacancy = crud.vacancy.update_vacancy(db=db, vacancy_id=vacancy_id, vacancy=vacancy_in)
    return vacancy

@router.delete("/{vacancy_id}")
def delete_vacancy(
    *,
    db: Session = Depends(deps.get_db),
    vacancy_id: int
):
    """
    Verwijder een vacature.
    """
    vacancy = crud.vacancy.get_vacancy(db=db, vacancy_id=vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacature niet gevonden")
    success = crud.vacancy.delete_vacancy(db=db, vacancy_id=vacancy_id)
    if not success:
        raise HTTPException(status_code=400, detail="Kon vacature niet verwijderen")
    return {"status": "success"}

@router.get("/municipality/{municipality_id}", response_model=List[Vacancy])
def read_vacancies_by_municipality(
    municipality_id: int,
    db: Session = Depends(deps.get_db)
):
    """
    Haal alle vacatures op voor een specifieke gemeente.
    """
    vacancies = crud.vacancy.get_vacancies_by_municipality(db=db, municipality_id=municipality_id)
    return vacancies

@router.get("/data/", response_model=List[Vacancy])
def read_data_vacancies(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Haal alle data-gerelateerde vacatures op.
    """
    vacancies = crud.vacancy.get_data_vacancies(db=db, skip=skip, limit=limit)
    return vacancies 