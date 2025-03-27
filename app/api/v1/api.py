from fastapi import APIRouter
from app.api.v1.endpoints import vacancies, municipalities, auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(vacancies.router, prefix="/vacancies", tags=["vacancies"])
api_router.include_router(municipalities.router, prefix="/municipalities", tags=["municipalities"]) 