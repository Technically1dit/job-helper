from google import genai
from google.genai import types
from backend.app.config import settings
from pydantic import BaseModel, Field
from typing import List, Optional

class ParsedResume(BaseModel):
    name: Optional[str] = None
    skills: List[str] = []
    experience: List[dict] = []
    education: List[dict] = []
    years_of_experience: int = 0
    preferred_roles: List[str] = []

class JobAnalysis(BaseModel):
    match_score: int = Field(description="Score from 0 to 100")
    recommendation: str = Field(description="strong_apply, apply, maybe, skip")
    matching_skills: List[str] = []
    missing_skills: List[str] = []
    short_summary: str = ""

class CompanySummary(BaseModel):
    company_summary: str = "Not available"
    industry: str = "Not available"
    company_size: str = "Not available"
    website: str = "Not available"

class ContactInfo(BaseModel):
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_role: Optional[str] = None
    contact_source: Optional[str] = None

class EmailDraft(BaseModel):
    subject: str
    body: str

def get_client():
    return genai.Client(api_key=settings.GEMINI_API_KEY)

def parse_resume(text: str) -> ParsedResume:
    client = get_client()
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=f"Extract structured profile data from this resume text. Do not invent any info. Resume:\n{text}",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ParsedResume,
            temperature=0.2
        )
    )
    return response.parsed

def analyze_job(profile_data: str, job_title: str, job_desc: str) -> JobAnalysis:
    client = get_client()
    contents = f"Analyze candidate against job. Candidate:\n{profile_data}\n\nJob: {job_title}\nDesc: {job_desc}"
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=JobAnalysis,
            temperature=0.2
        )
    )
    return response.parsed

def summarize_company(company: str, search_results: str) -> CompanySummary:
    client = get_client()
    contents = f"Summarize {company} ONLY using these search results. Do not invent. Use 'Not available' if missing.\n\n{search_results}"
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CompanySummary,
            temperature=0.2
        )
    )
    return response.parsed

def extract_contact(company: str, search_results: str) -> ContactInfo:
    client = get_client()
    contents = f"Extract a verified recruitment email for {company} ONLY if it appears exactly in these search results. Do not invent emails. Return null if not found.\n\n{search_results}"
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ContactInfo,
            temperature=0.0
        )
    )
    return response.parsed

def generate_email(profile: str, job_title: str, company: str, contact_name: str) -> EmailDraft:
    client = get_client()
    contents = f"Write a concise (100-180 words) professional application email for {job_title} at {company}. Contact: {contact_name or 'Hiring Team'}. Candidate Info: {profile}. Do not hallucinate."
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=EmailDraft,
            temperature=0.3
        )
    )
    return response.parsed
