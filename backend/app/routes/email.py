from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from backend.app.database import get_db
from backend.app.models.gmail import GmailAccount
from backend.app.models.application import Application
from backend.app.auth import get_current_user
from backend.app.services.crypto import decrypt, encrypt
from backend.app.services.gmail_service import send_gmail_message, refresh_gmail_token
from pydantic import BaseModel

router = APIRouter(prefix="/api/email", tags=["email"])

class EmailSendRequest(BaseModel):
    job_id: int
    to: str
    subject: str
    body: str

@router.post("/send")
async def send_email_endpoint(req: EmailSendRequest, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    acc = db.query(GmailAccount).filter(GmailAccount.user_id == user["id"]).first()
    if not acc: raise HTTPException(status_code=400, detail="Gmail not connected")
    
    access_token = decrypt(acc.encrypted_access_token)
    if not access_token or acc.token_expiry < datetime.utcnow():
        if not acc.encrypted_refresh_token:
            raise HTTPException(status_code=400, detail="Gmail disconnected. Reconnect needed.")
        refresh_token = decrypt(acc.encrypted_refresh_token)
        new_tokens = await refresh_gmail_token(refresh_token)
        access_token = new_tokens["access_token"]
        acc.encrypted_access_token = encrypt(access_token)
        db.commit()
        
    await send_gmail_message(access_token, req.to, req.subject, req.body)
    
    app = Application(
        user_id=user["id"],
        job_id=req.job_id,
        recipient=req.to,
        subject=req.subject,
        body=req.body,
        status="Applied",
        sent_at=datetime.utcnow()
    )
    db.add(app)
    db.commit()
    return {"status": "sent"}
