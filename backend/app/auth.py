from fastapi import Request, HTTPException, Security
from fastapi.security import APIKeyCookie
from jose import JWTError, jwt
from datetime import datetime, timedelta
from backend.app.config import settings

ALGORITHM = "HS256"
cookie_sec = APIKeyCookie(name="session_jwt")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SESSION_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(request: Request):
    token = request.cookies.get("session_jwt")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, settings.SESSION_SECRET, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid auth credentials")
        return {"id": int(user_id), "email": payload.get("email")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid auth credentials")
