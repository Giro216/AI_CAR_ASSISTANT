from fastapi import FastAPI

try:
	from dotenv import load_dotenv
except Exception:  # pragma: no cover - fallback для окружений без python-dotenv
	load_dotenv = None

if load_dotenv is not None:
	load_dotenv()


app = FastAPI(title="Service Authentication", version="0.1.0")

# API v1
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])

