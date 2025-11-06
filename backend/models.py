"""Database models and API response models for the Patrimoniu application."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import List

Base = declarative_base()


class Monument(Base):
    """Monument model representing historical monuments."""
    __tablename__ = "monuments"
    
    lmi_code = Column(String, primary_key=True, index=True)
    id = Column(Integer, nullable=False)
    county = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    city = Column(String, nullable=False, index=True)
    address = Column(String)
    dating = Column(String)


# Pydantic models for API responses
class MonumentResponse(BaseModel):
    """Response model for a single monument."""
    id: int
    lmi_code: str
    name: str
    city: str
    address: str | None
    dating: str | None
    county: str

    class Config:
        from_attributes = True


class PaginatedMonumentsResponse(BaseModel):
    """Response model for paginated monuments list."""
    count: int
    page: int
    page_size: int
    total_pages: int
    results: List[MonumentResponse]

