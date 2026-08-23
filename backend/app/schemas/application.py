from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ApplicationCreate(BaseModel):
    job_id: int
    recipient: str
    subject: str
    body: str

class ApplicationUpdate(BaseModel):
    status: str

class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    recipient: str
    subject: str
    body: str
    status: str
    created_at: datetime
    sent_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
