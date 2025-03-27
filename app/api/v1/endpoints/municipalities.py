from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import crud
from app.api import deps
from app.schemas.municipality import Municipality, MunicipalityCreate, MunicipalityUpdate

router = APIRouter()

@router.get("/", response_model=List[Municipality])
def read_municipalities(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True
):
    """
    Haal alle gemeenten op met optionele filters.
    """
    municipalities = crud.municipality.get_municipalities(
        db,
        skip=skip,
        limit=limit,
        active_only=active_only
    )
    return municipalities

@router.post("/", response_model=Municipality)
def create_municipality(
    *,
    db: Session = Depends(deps.get_db),
    municipality_in: MunicipalityCreate
):
    """
    Maak een nieuwe gemeente aan.
    """
    municipality = crud.municipality.get_municipality_by_name(db, name=municipality_in.name)
    if municipality:
        raise HTTPException(
            status_code=400,
            detail="Een gemeente met deze naam bestaat al."
        )
    municipality = crud.municipality.create_municipality(db=db, municipality=municipality_in)
    return municipality

@router.get("/{municipality_id}", response_model=Municipality)
def read_municipality(
    municipality_id: int,
    db: Session = Depends(deps.get_db)
):
    """
    Haal een specifieke gemeente op door ID.
    """
    municipality = crud.municipality.get_municipality(db=db, municipality_id=municipality_id)
    if not municipality:
        raise HTTPException(status_code=404, detail="Gemeente niet gevonden")
    return municipality

@router.put("/{municipality_id}", response_model=Municipality)
def update_municipality(
    *,
    db: Session = Depends(deps.get_db),
    municipality_id: int,
    municipality_in: MunicipalityUpdate
):
    """
    Update een gemeente.
    """
    municipality = crud.municipality.get_municipality(db=db, municipality_id=municipality_id)
    if not municipality:
        raise HTTPException(status_code=404, detail="Gemeente niet gevonden")
    municipality = crud.municipality.update_municipality(
        db=db,
        municipality_id=municipality_id,
        municipality=municipality_in
    )
    return municipality

@router.delete("/{municipality_id}")
def delete_municipality(
    *,
    db: Session = Depends(deps.get_db),
    municipality_id: int
):
    """
    Verwijder een gemeente.
    """
    municipality = crud.municipality.get_municipality(db=db, municipality_id=municipality_id)
    if not municipality:
        raise HTTPException(status_code=404, detail="Gemeente niet gevonden")
    success = crud.municipality.delete_municipality(db=db, municipality_id=municipality_id)
    if not success:
        raise HTTPException(status_code=400, detail="Kon gemeente niet verwijderen")
    return {"status": "success"}

@router.get("/active/", response_model=List[Municipality])
def read_active_municipalities(
    db: Session = Depends(deps.get_db)
):
    """
    Haal alle actieve gemeenten op.
    """
    municipalities = crud.municipality.get_active_municipalities(db=db)
    return municipalities 