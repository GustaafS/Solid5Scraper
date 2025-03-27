from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Municipality(Base):
    __tablename__ = "municipalities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    website = Column(String(255))
    vacancy_page_url = Column(String(512))
    latitude = Column(Float)
    longitude = Column(Float)
    last_scraped = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Relaties
    vacancies = relationship("Vacancy", back_populates="municipality_rel") 