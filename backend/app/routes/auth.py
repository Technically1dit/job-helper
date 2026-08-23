from fastapi import APIRouter, Depends, Request, Response, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode
import httpx
import secrets

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas.user import UserResponse
from backend.app.auth import create_access_token, get_current_user
from backend.app.config import settings


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/google")
async def login_google(response: Response):
    state = secrets.token_urlsafe(32)

    is_production = settings.BACKEND_URL.startswith("https://")

    response.set_cookie(
        "oauth_state",
        state,
        httponly=True,
        secure=is_production,
        samesite="lax",
        max_age=300,
    )

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
    }

    url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        + urlencode(params)
    )

    return {"url": url}


@router.get("/google/callback")
async def auth_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    saved_state = request.cookies.get("oauth_state")

    if not saved_state or saved_state != state:
        raise HTTPException(
            status_code=400,
            detail="Invalid state",
        )

    data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
    }

    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://oauth2.googleapis.com/token",
            data=data,
        )

        token_res.raise_for_status()

        token_data = token_res.json()
        access_token = token_data["access_token"]

        user_res = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={
                "Authorization": f"Bearer {access_token}"
            },
        )

        user_res.raise_for_status()
        user_info = user_res.json()

    user = (
        db.query(User)
        .filter(User.email == user_info["email"])
        .first()
    )

    if not user:
        user = User(
            google_id=user_info["id"],
            email=user_info["email"],
            name=user_info.get("name", ""),
            profile_picture=user_info.get("picture", ""),
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    jwt_token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
        }
    )

    is_production = settings.BACKEND_URL.startswith("https://")

    response = RedirectResponse(
        url=f"{settings.FRONTEND_URL}/"
    )

    response.set_cookie(
        "session_jwt",
        jwt_token,
        httponly=True,
        secure=is_production,
        samesite="lax",
    )

    response.delete_cookie("oauth_state")

    return response


@router.get("/me", response_model=UserResponse)
def get_me(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_user = (
        db.query(User)
        .filter(User.id == user["id"])
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return db_user


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("session_jwt")
    return {"status": "ok"}