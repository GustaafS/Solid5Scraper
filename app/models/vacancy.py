from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum

class FunctionCategory(str, enum.Enum):
    IT = "IT"
    FINANCE = "Finance"
    HR = "HR"
    DATA = "Data"
    MANAGEMENT = "Management"
    OTHER = "Other"

class EducationLevel(str, enum.Enum):
    MBO = "MBO"
    HBO = "HBO"
    WO = "WO"
    OTHER = "Other"

class Vacancy(Base):
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    municipality = Column(String(255), nullable=False)
    salary_scale = Column(String(50))
    education_level = Column(Enum(EducationLevel))
    function_category = Column(Enum(FunctionCategory))
    publication_date = Column(DateTime)
    closing_date = Column(DateTime)
    description = Column(Text)
    url = Column(String(512), unique=True)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Relaties
    municipality_id = Column(Integer, ForeignKey("municipalities.id"))
    municipality_rel = relationship("Municipality", back_populates="vacancies")
    
    # Extra velden voor datafuncties
    data_tools = Column(String(255))  # Komma-gescheiden lijst van tools
    data_experience_years = Column(Integer)
    data_certifications = Column(String(255))  # Komma-gescheiden lijst van certificeringen 