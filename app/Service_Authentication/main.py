import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.router import api_router
from app.core.database import engine, Base

logger = logging.getLogger("auth_service")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
	title=settings.PROJECT_NAME,
	openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["health"])
async def health_check():
	return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)