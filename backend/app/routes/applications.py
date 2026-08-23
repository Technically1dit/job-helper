from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.models.application import Application
from backend.app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from backend.app.auth import get_current_user

router = APIRouter(prefix="/api/applications", tags=["applications"])

@router.get("", response_model=List[ApplicationResponse])
def list_applications(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Application).filter(Application.user_id == user["id"]).order_by(Application.created_at.desc()).all()

@router.post("", response_model=ApplicationResponse)
def create_application(app: ApplicationCreate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    new_app = Application(**app.dict(), user_id=user["id"])
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return new_app

@router.patch("/{app_id}", response_model=ApplicationResponse)
def update_application(app_id: int, app: ApplicationUpdate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    db_app = db.query(Application).filter(Application.id == app_id, Application.user_id == user["id"]).first()
    if not db_app: raise HTTPException(status_code=404)
    db_app.status = app.status
    db.commit()
    db.refresh(db_app)
    return db_app
