from src.core.config import settings
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker


if settings().environment == "local":
    SQLALCHEMY_DATABASE_URL = f"postgresql://{settings().database.user}:{settings().database.password}@{settings().database.host}:{settings().database.port}/{settings().database.db}"


def init_engine():
    return create_engine(SQLALCHEMY_DATABASE_URL)


engine = init_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
