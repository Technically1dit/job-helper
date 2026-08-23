from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import hashlib

from backend.app.database import get_db
from backend.app.models.job import Job
from backend.app.models.profile import Profile
from backend.app.models.notification import Notification
from backend.app.schemas.job import JobSearchRequest, JobResponse
from backend.app.auth import get_current_user
from backend.app.services import serpapi, gemini

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

def make_fingerprint(user_id, title, company, location):
    s = f"{user_id}:{str(title).lower()}:{str(company).lower()}:{str(location).lower()}"
    return hashlib.md5(s.encode()).hexdigest()

@router.post("/search", response_model=List[JobResponse])
async def search_jobs_endpoint(req: JobSearchRequest, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    results = await serpapi.search_jobs(req.query, req.location)
    
    new_jobs = []
    for r in results:
        title = r.get("title", "Unknown")
        company = r.get("company_name", "Unknown")
        location = r.get("location", "Unknown")
        fp = make_fingerprint(user["id"], title, company, location)
        
        existing = db.query(Job).filter(Job.fingerprint == fp).first()
        if not existing:
            job = Job(
                user_id=user["id"],
                title=title,
                company=company,
                location=location,
                description=r.get("description", ""),
                source=r.get("via", "Web"),
                source_url=r.get("share_link", ""),
                fingerprint=fp
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            new_jobs.append(job)
            
            notif = Notification(user_id=user["id"], job_id=job.id, title="New Job Found", message=f"{title} at {company}")
            db.add(notif)
            db.commit()
            
    return db.query(Job).filter(Job.user_id == user["id"]).order_by(Job.created_at.desc()).limit(50).all()

@router.get("", response_model=List[JobResponse])
def list_jobs(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Job).filter(Job.user_id == user["id"]).order_by(Job.created_at.desc()).all()

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user["id"]).first()
    if not job:
        raise HTTPException(status_code=404)
    return job

@router.post("/{job_id}/analyze")
def analyze_job_endpoint(job_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user["id"]).first()
    profile = db.query(Profile).filter(Profile.user_id == user["id"]).first()
    if not job or not profile:
        raise HTTPException(status_code=404)
        
    prof_str = f"Skills: {profile.skills}\nExperience: {profile.experience}"
    analysis = gemini.analyze_job(prof_str, job.title, job.description or "")
    
    job.match_score = analysis.match_score
    job.analysis = analysis.dict()
    db.commit()
    db.refresh(job)
    return job

@router.post("/{job_id}/company")
async def summarize_company_endpoint(job_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user["id"]).first()
    if not job: raise HTTPException(status_code=404)
    
    results = await serpapi.search_company_info(job.company)
    res_str = "\n".join([f"{r.get('title')}: {r.get('snippet')}" for r in results])
    
    summary = gemini.summarize_company(job.company, res_str)
    job.company_summary = summary.company_summary
    job.industry = summary.industry
    job.company_website = summary.website
    db.commit()
    return job

@router.post("/{job_id}/contact")
async def extract_contact_endpoint(job_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user["id"]).first()
    if not job: raise HTTPException(status_code=404)
    
    results = await serpapi.search_contact_info(job.company)
    res_str = "\n".join([f"{r.get('title')}: {r.get('snippet')}" for r in results])
    
    contact = gemini.extract_contact(job.company, res_str)
    job.contact_name = contact.contact_name
    job.contact_email = contact.contact_email
    job.contact_role = contact.contact_role
    job.contact_source = contact.contact_source
    db.commit()
    return job

@router.post("/{job_id}/generate-email")
def generate_email_endpoint(job_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user["id"]).first()
    profile = db.query(Profile).filter(Profile.user_id == user["id"]).first()
    if not job or not profile: raise HTTPException(status_code=404)
    
    prof_str = f"Skills: {profile.skills}\nExperience: {profile.experience}"
    draft = gemini.generate_email(prof_str, job.title, job.company, job.contact_name or "")
    return draft

@router.post("/{job_id}/save")
def toggle_save_job(job_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user["id"]).first()
    if not job: raise HTTPException(status_code=404)
    if job.saved_at:
        job.saved_at = None
    else:
        job.saved_at = datetime.utcnow()
    db.commit()
    db.refresh(job)
    return job
