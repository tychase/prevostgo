from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .database import Base

class Coach(Base):
    __tablename__ = "coaches"
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)  # e.g., listing URL or hash
    url = Column(String, index=True)
    title = Column(String, index=True)
    year = Column(Integer, index=True)
    model = Column(String, index=True)
    price = Column(Float, index=True)
    location = Column(String, index=True)
    specs = Column(JSONB, default=dict)  # normalized key/values
    features = Column(JSONB, default=list)  # list of strings
    photos = Column(JSONB, default=list)    # list of urls
    seller = Column(JSONB, default=dict)    # name/phone/email if parsed
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
