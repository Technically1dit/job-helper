from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProfileUpdate(BaseModel):
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    skills: List[str] = []
    experience: List[dict] = []
    education: List[dict] = []
    years_of_experience: int = 0
    preferred_roles: List[str] = []
    preferred_locations: List[str] = []
    preferred_employment_type: Optional[str] = None

class ProfileResponse(ProfileUpdate):
    id: int
    user_id: int
    resume_filename: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
