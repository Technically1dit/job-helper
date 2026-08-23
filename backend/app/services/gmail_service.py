import httpx
from backend.app.config import settings
import base64
from email.message import EmailMessage

async def get_gmail_tokens(code: str):
    data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.GMAIL_REDIRECT_URI,
    }
    async with httpx.AsyncClient() as client:
        res = await client.post("https://oauth2.googleapis.com/token", data=data)
        res.raise_for_status()
        return res.json()

async def refresh_gmail_token(refresh_token: str):
    data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    async with httpx.AsyncClient() as client:
        res = await client.post("https://oauth2.googleapis.com/token", data=data)
        res.raise_for_status()
        return res.json()

async def send_gmail_message(access_token: str, to: str, subject: str, body: str):
    msg = EmailMessage()
    msg.set_content(body)
    msg["To"] = to
    msg["Subject"] = subject

    encoded_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {"raw": encoded_message}
    
    async with httpx.AsyncClient() as client:
        res = await client.post("https://gmail.googleapis.com/gmail/v1/users/me/messages/send", headers=headers, json=payload)
        res.raise_for_status()
        return res.json()
