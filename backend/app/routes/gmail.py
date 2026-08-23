from fastapi import APIRouter, Depends, Request, Response, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets

from backend.app.database import get_db
from backend.app.models.gmail import GmailAccount
from backend.app.auth import get_current_user
from backend.app.config import settings
from backend.app.services.crypto import encrypt
from backend.app.services.gmail_service import get_gmail_tokens

router = APIRouter(prefix="/api/gmail", tags=["gmail"])

@router.get("/connect")
def connect_gmail(response: Response, user: dict = Depends(get_current_user)):
    state = secrets.token_urlsafe(32)
    response.set_cookie("gmail_state", state, httponly=True, secure=True, samesite="lax", max_age=300)
    url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={settings.GMAIL_REDIRECT_URI}&response_type=code&scope=https://www.googleapis.com/auth/gmail.send&access_type=offline&prompt=consent&state={state}"
    return {"url": url}

from fastapi.responses import RedirectResponse

@router.get("/callback")
async def gmail_callback(request: Request, code: str, state: str, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    saved_state = request.cookies.get("gmail_state")
    if not saved_state or saved_state != state:
        raise HTTPException(status_code=400, detail="Invalid state")
        
    tokens = await get_gmail_tokens(code)
    
    # Needs email, but we already have it from current_user
    acc = db.query(GmailAccount).filter(GmailAccount.user_id == user["id"]).first()
    if not acc:
        acc = GmailAccount(user_id=user["id"], email=user["email"])
        db.add(acc)
    
    acc.encrypted_access_token = encrypt(tokens["access_token"])
    if "refresh_token" in tokens:
        acc.encrypted_refresh_token = encrypt(tokens["refresh_token"])
    acc.token_expiry = datetime.utcnow() + timedelta(seconds=tokens.get("expires_in", 3599))
    
    db.commit()
    response = RedirectResponse(url=f"{settings.FRONTEND_URL}/gmail")
    response.delete_cookie("gmail_state")
    return response

@router.get("/status")
def gmail_status(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    acc = db.query(GmailAccount).filter(GmailAccount.user_id == user["id"]).first()
    if acc: return {"connected": True, "email": acc.email}
    return {"connected": False}

@router.post("/disconnect")
def gmail_disconnect(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(GmailAccount).filter(GmailAccount.user_id == user["id"]).delete()
    db.commit()
    return {"status": "disconnected"}
