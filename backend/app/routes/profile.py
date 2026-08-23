from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.profile import Profile
from backend.app.schemas.profile import ProfileUpdate, ProfileResponse
from backend.app.auth import get_current_user
from backend.app.services.resume import extract_text_from_pdf
from backend.app.services.gemini import parse_resume

router = APIRouter(prefix="/api/profile", tags=["profile"])

@router.get("", response_model=ProfileResponse)
def get_profile(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user["id"]).first()
    if not profile:
        profile = Profile(user_id=user["id"])
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.put("", response_model=ProfileResponse)
def update_profile(profile_data: ProfileUpdate, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user["id"]).first()
    if not profile:
        profile = Profile(user_id=user["id"])
        db.add(profile)
    
    for key, value in profile_data.dict().items():
        setattr(profile, key, value)
        
    db.commit()
    db.refresh(profile)
    return profile

@router.post("/resume", response_model=ProfileResponse)
async def upload_resume(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF allowed")

    contents = await file.read()

    if len(contents) > 4.5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")

    text = extract_text_from_pdf(contents)
    parsed = parse_resume(text)

    profile = db.query(Profile).filter(
        Profile.user_id == user["id"]
    ).first()

    profile.resume_text = text
    profile.resume_filename = file.filename

    if parsed.skills:
        profile.skills = list(parsed.skills)

    if parsed.experience:
        profile.experience = [
            item.model_dump() if hasattr(item, "model_dump") else item
            for item in parsed.experience
        ]

    if parsed.education:
        profile.education = [
            item.model_dump() if hasattr(item, "model_dump") else item
            for item in parsed.education
        ]

    if parsed.years_of_experience:
        profile.years_of_experience = parsed.years_of_experience

    db.commit()
    db.refresh(profile)

    return profile