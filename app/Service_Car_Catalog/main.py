from fastapi import FastAPI

from app.api.v1.cars import router as cars_router

try:
	from dotenv import load_dotenv
except Exception:  # pragma: no cover - fallback для окружений без python-dotenv
	load_dotenv = None

if load_dotenv is not None:
	load_dotenv()


app = FastAPI(title="Service Car Catalog", version="0.1.0")

# API v1
app.include_router(cars_router, prefix="/api/v1/cars", tags=["cars"])

