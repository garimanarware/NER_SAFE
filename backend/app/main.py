from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.locations import router as locations_router
from backend.app.api.forecasts import router as forecasts_router
from backend.app.api.alerts import router as alerts_router
from backend.app.api.terrain import router as terrain_router
from backend.app.api.site_risk import router as site_risk_router

app = FastAPI(
    title="NER-SAFE API",
    description="Disaster Intelligence Platform for the North Eastern Region",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(locations_router)
app.include_router(forecasts_router)
app.include_router(alerts_router)
app.include_router(terrain_router)
app.include_router(site_risk_router)


@app.get("/")
def root():
    return {
        "message": "NER-SAFE backend is running",
        "status": "online"
    }