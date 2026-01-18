from fastapi import FastAPI
from app.routers import router as flight_router
app = FastAPI(
    title="Fast Flight API",
    description="Flight On Time",
    version="0.0.1",
)
app.include_router(flight_router)
