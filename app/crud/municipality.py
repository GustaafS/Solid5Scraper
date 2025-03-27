from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.municipality import Municipality
from app.schemas.municipality import MunicipalityCreate, MunicipalityUpdate
from datetime import datetime

def get_municipality(db: Session, municipality_id: int) -> Optional[Municipality]:
    return db.query(Municipality).filter(Municipality.id == municipality_id).first()

def get_municipality_by_name(db: Session, name: str) -> Optional[Municipality]:
    return db.query(Municipality).filter(Municipality.name == name).first()

def get_municipalities(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True
) -> List[Municipality]:
    query = db.query(Municipality)
    if active_only:
        query = query.filter(Municipality.is_active == True)
    return query.offset(skip).limit(limit).all()

def create_municipality(db: Session, municipality: MunicipalityCreate) -> Municipality:
    db_municipality = Municipality(**municipality.model_dump())
    db.add(db_municipality)
    db.commit()
    db.refresh(db_municipality)
    return db_municipality

def update_municipality(
    db: Session,
    municipality_id: int,
    municipality: MunicipalityUpdate
) -> Optional[Municipality]:
    db_municipality = get_municipality(db, municipality_id)
    if not db_municipality:
        return None
    
    for field, value in municipality.model_dump(exclude_unset=True).items():
        setattr(db_municipality, field, value)
    
    db.commit()
    db.refresh(db_municipality)
    return db_municipality

def delete_municipality(db: Session, municipality_id: int) -> bool:
    db_municipality = get_municipality(db, municipality_id)
    if not db_municipality:
        return False
    
    db.delete(db_municipality)
    db.commit()
    return True

def update_last_scraped(db: Session, municipality_id: int) -> Optional[Municipality]:
    db_municipality = get_municipality(db, municipality_id)
    if not db_municipality:
        return None
    
    db_municipality.last_scraped = datetime.utcnow()
    db.commit()
    db.refresh(db_municipality)
    return db_municipality

def get_active_municipalities(db: Session) -> List[Municipality]:
    return db.query(Municipality).filter(Municipality.is_active == True).all() 