from typing import Generator
from .config import SessionLocal

# Dependency


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
