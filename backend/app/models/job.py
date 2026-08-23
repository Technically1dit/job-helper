from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from backend.app.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    company = Column(String)
    location = Column(String)
    description = Column(String, nullable=True)
    source = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    posted_at = Column(String, nullable=True)
    salary = Column(String, nullable=True)
    job_type = Column(String, nullable=True)
    source_logo = Column(String, nullable=True)
    raw_data = Column(JSON, nullable=True)
    
    match_score = Column(Integer, nullable=True)
    analysis = Column(JSON, nullable=True)
    
    company_summary = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    company_website = Column(String, nullable=True)
    
    contact_name = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    contact_role = Column(String, nullable=True)
    contact_source = Column(String, nullable=True)
    
    fingerprint = Column(String, unique=True, index=True)
    
    saved_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
