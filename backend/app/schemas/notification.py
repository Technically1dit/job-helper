from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationResponse(BaseModel):
    id: int
    job_id: Optional[int] = None
    title: str
    message: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
