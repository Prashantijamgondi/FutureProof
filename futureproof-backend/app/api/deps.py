from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db

def get_current_db() -> Generator:
    """Get database session"""
    try:
        db = get_db()
        yield db
    finally:
        pass
