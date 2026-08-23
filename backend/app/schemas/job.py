from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class JobSearchRequest(BaseModel):
    query: str
    location: str

class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    apply_url: Optional[str] = None
    external_id: Optional[str] = None
    remote: Optional[bool] = None
    skills: List[str] = []
    experience_required: Optional[str] = None
    posted_at: Optional[str] = None
    salary: Optional[str] = None
    job_type: Optional[str] = None
    match_score: Optional[int] = None
    analysis: Optional[Dict[str, Any]] = None
    company_summary: Optional[str] = None
    industry: Optional[str] = None
    company_website: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_role: Optional[str] = None
    saved_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
