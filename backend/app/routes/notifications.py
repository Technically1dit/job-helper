from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.models.notification import Notification
from backend.app.schemas.notification import NotificationResponse
from backend.app.auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@router.get("", response_model=List[NotificationResponse])
def get_notifications(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Notification).filter(Notification.user_id == user["id"]).order_by(Notification.created_at.desc()).limit(20).all()

@router.patch("/{notif_id}/read")
def read_notification(notif_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == user["id"]).first()
    if not notif: raise HTTPException(status_code=404)
    notif.is_read = True
    db.commit()
    return {"status": "ok"}
