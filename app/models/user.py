from sqlalchemy import Boolean, Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum

class UserRole(str, enum.Enum):
    FREE = "free"
    PREMIUM = "premium"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.FREE)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Relaties
    saved_vacancies = relationship("SavedVacancy", back_populates="user") 