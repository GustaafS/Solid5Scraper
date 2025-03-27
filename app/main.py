from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Nederlandse Gemeentelijke Vacaturetracker",
    description="API voor het tracken van vacatures bij Nederlandse gemeenten",
    version="1.0.0"
)

# CORS configuratie
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In productie moet dit beperkt worden tot specifieke domeinen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welkom bij de Nederlandse Gemeentelijke Vacaturetracker API",
        "status": "online"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    } 