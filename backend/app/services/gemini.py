from google import genai
from google.genai import types
from backend.app.config import settings
from pydantic import BaseModel, Field
from typing import List, Optional


# ============================================================
# Resume Parsing Models
# ============================================================

class ExperienceItem(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class EducationItem(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class ParsedResume(BaseModel):
    name: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    years_of_experience: int = 0
    preferred_roles: List[str] = Field(default_factory=list)


# ============================================================
# Job Analysis
# ============================================================

class JobAnalysis(BaseModel):
    match_score: int = Field(
        description="Score from 0 to 100"
    )
    recommendation: str = Field(
        description="strong_apply, apply, maybe, skip"
    )
    matching_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    short_summary: str = ""


# ============================================================
# Company Summary
# ============================================================

class CompanySummary(BaseModel):
    company_summary: str = "Not available"
    industry: str = "Not available"
    company_size: str = "Not available"
    website: str = "Not available"


# ============================================================
# Contact Information
# ============================================================

class ContactInfo(BaseModel):
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_role: Optional[str] = None
    contact_source: Optional[str] = None


# ============================================================
# Email Draft
# ============================================================

class EmailDraft(BaseModel):
    subject: str
    body: str


# ============================================================
# Gemini Client
# ============================================================

def get_client():
    return genai.Client(
        api_key=settings.GEMINI_API_KEY
    )


# ============================================================
# Resume Parser
# ============================================================

def parse_resume(text: str) -> ParsedResume:
    client = get_client()

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=(
            "Extract structured profile data from this resume text. "
            "Do not invent any information. "
            "Only extract information explicitly present in the resume.\n\n"
            f"Resume:\n{text}"
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ParsedResume,
            temperature=0.2,
        ),
    )

    return response.parsed


# ============================================================
# Job Analysis
# ============================================================

def analyze_job(
    profile_data: str,
    job_title: str,
    job_desc: str
) -> JobAnalysis:

    client = get_client()

    contents = (
        f"Analyze the candidate against the job.\n\n"
        f"Candidate:\n{profile_data}\n\n"
        f"Job: {job_title}\n\n"
        f"Description:\n{job_desc}"
    )

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=JobAnalysis,
            temperature=0.2,
        ),
    )

    return response.parsed


# ============================================================
# Company Summary
# ============================================================

def summarize_company(
    company: str,
    search_results: str
) -> CompanySummary:

    client = get_client()

    contents = (
        f"Summarize {company} ONLY using these search results. "
        "Do not invent information. "
        "Use 'Not available' if information is missing.\n\n"
        f"{search_results}"
    )

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CompanySummary,
            temperature=0.2,
        ),
    )

    return response.parsed


# ============================================================
# Contact Extraction
# ============================================================

def extract_contact(
    company: str,
    search_results: str
) -> ContactInfo:

    client = get_client()

    contents = (
        f"Extract a verified recruitment email for {company} "
        "ONLY if it appears exactly in these search results. "
        "Do not invent emails. "
        "Return null if not found.\n\n"
        f"{search_results}"
    )

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ContactInfo,
            temperature=0.0,
        ),
    )

    return response.parsed


# ============================================================
# Email Generation
# ============================================================

def generate_email(
    profile: str,
    job_title: str,
    company: str,
    contact_name: str
) -> EmailDraft:

    client = get_client()

    contents = (
        f"Write a concise (100-180 words) professional "
        f"application email for {job_title} at {company}. "
        f"Contact: {contact_name or 'Hiring Team'}.\n\n"
        f"Candidate Info:\n{profile}\n\n"
        "Do not hallucinate information."
    )

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=EmailDraft,
            temperature=0.3,
        ),
    )

    return response.parsed