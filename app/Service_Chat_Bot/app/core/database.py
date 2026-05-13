import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv(
	"DATABASE_URL",
	"postgresql+psycopg2://postgres:password@localhost:5432/ai_assistant_chat_memory",
)

engine = create_engine(
	DATABASE_URL,
	pool_pre_ping=True,
	pool_size=5,
	max_overflow=10,
	echo=False,
)

SessionLocal = sessionmaker(
	autocommit=False,
	autoflush=False,
	bind=engine,
)

Base = declarative_base()

