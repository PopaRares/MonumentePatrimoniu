"""Database models for the Patrimoniu application."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

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

