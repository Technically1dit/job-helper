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
from backend.app.services.jobs import JobSearchUnavailable, search_jobs
from backend.app.services.jobs.contacts import recruitment_role_supported, verified_email_from_source
from backend.app.services.jobs.ranking import score_job

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

def make_fingerprint(user_id, title, company, location):
    s = f"{user_id}:{str(title).lower()}:{str(company).lower()}:{str(location).lower()}"
    return hashlib.md5(s.encode()).hexdigest()

@router.post("/search", response_model=List[JobResponse])
async def search_jobs_endpoint(req: JobSearchRequest, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        outcome = await search_jobs(req.query, req.location)
    except JobSearchUnavailable:
        raise HTTPException(status_code=503, detail="Job search providers are temporarily unavailable.")
    
    searched_jobs = []
    profile = db.query(Profile).filter(Profile.user_id == user["id"]).first()
    for r in outcome.jobs:
        title = r["title"]
        company = r["company_name"]
        location = r.get("location", "Unknown")
        fp = make_fingerprint(user["id"], title, company, location)
        match_score, analysis = score_job(r, profile)
        
        existing = db.query(Job).filter(Job.fingerprint == fp).first()
        if not existing:
            job = Job(
                user_id=user["id"],
                title=title,
                company=company,
                location=location,
                description=r.get("description", ""),
                source=r.get("source", "Web"),
                source_url=r.get("source_url") or r.get("apply_url") or "",
                posted_at=r.get("posted_at"),
                job_type=r.get("job_type"),
                raw_data=r,
                match_score=match_score,
                analysis=analysis,
                fingerprint=fp
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            searched_jobs.append(job)
            
            notif = Notification(user_id=user["id"], job_id=job.id, title="New Job Found", message=f"{title} at {company}")
            db.add(notif)
            db.commit()
        else:
            # Preserve the existing record but refresh provider URLs/details.
            existing.source_url = r.get("source_url") or r.get("apply_url") or existing.source_url
            existing.raw_data = r
            existing.match_score = match_score
            existing.analysis = analysis
            db.commit()
            searched_jobs.append(existing)
            
    # Return this search only. The full history remains available through GET /jobs.
    return searched_jobs

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
    job.contact_email = verified_email_from_source(contact.contact_email, res_str)
    # A generic address is not called an HR/recruitment contact without
    # supporting context in the retrieved source.
    job.contact_role = contact.contact_role if job.contact_email and recruitment_role_supported(job.contact_email, res_str) else None
    job.contact_source = contact.contact_source if job.contact_email else None
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
