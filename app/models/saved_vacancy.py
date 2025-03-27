from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime

class SavedVacancy(Base):
    __tablename__ = "saved_vacancies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), nullable=False)
    saved_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaties
    user = relationship("User", back_populates="saved_vacancies")
    vacancy = relationship("Vacancy") 