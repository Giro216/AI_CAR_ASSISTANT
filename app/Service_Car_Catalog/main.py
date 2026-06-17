from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.cars import router as cars_router

try:
	from dotenv import load_dotenv
except Exception:
	load_dotenv = None

if load_dotenv is not None:
	load_dotenv()

app = FastAPI(title="Service Car Catalog", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1
app.include_router(cars_router, prefix="/api/v1/cars", tags=["cars"])


@app.get("/health", tags=["health"])
async def health_check():
	return {"status": "healthy"}
