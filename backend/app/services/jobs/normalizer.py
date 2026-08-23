from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse, urlunparse
import re


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    value = " ".join(str(value).split())
    return value or None


def canonical_url(url: Any) -> str | None:
    value = clean_text(url)
    if not value:
        return None
    try:
        parsed = urlparse(value)
        if not parsed.scheme or not parsed.netloc:
            return value
        return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path.rstrip("/"), "", "", ""))
    except ValueError:
        return value


def normalize_job(raw: dict[str, Any], provider: str) -> dict[str, Any] | None:
    """Convert a provider payload without fabricating fields."""
    title = clean_text(raw.get("title") or raw.get("job_title"))
    company = clean_text(raw.get("company_name") or raw.get("company") or raw.get("company_name_display"))
    if not title or not company:
        return None
    apply_url = canonical_url(raw.get("apply_url") or raw.get("application_url") or raw.get("job_url") or raw.get("share_link"))
    source_url = canonical_url(raw.get("source_url") or raw.get("share_link") or raw.get("job_url") or apply_url)
    skills = raw.get("skills") or []
    if isinstance(skills, str):
        skills = [part.strip() for part in skills.split(",") if part.strip()]
    if not isinstance(skills, list):
        skills = []
    return {
        "external_id": clean_text(raw.get("external_id") or raw.get("job_id") or raw.get("id")),
        "title": title,
        "company_name": company,
        "location": clean_text(raw.get("location") or raw.get("job_location")) or "Not specified",
        "description": clean_text(raw.get("description") or raw.get("job_description")),
        "employment_type": clean_text(raw.get("employment_type") or raw.get("job_type")),
        "experience_required": clean_text(raw.get("experience_required")),
        "salary_min": raw.get("salary_min"),
        "salary_max": raw.get("salary_max"),
        "salary_currency": clean_text(raw.get("salary_currency")),
        "remote": bool(raw.get("remote")) or "remote" in (clean_text(raw.get("location")) or "").casefold(),
        "posted_at": clean_text(raw.get("posted_at") or (raw.get("detected_extensions", {}).get("posted_at") if isinstance(raw.get("detected_extensions"), dict) else None)),
        "source": clean_text(raw.get("source") or raw.get("via")) or provider,
        "provider": provider,
        "source_url": source_url,
        "apply_url": apply_url,
        "skills": [clean_text(item) for item in skills if clean_text(item)],
        "job_type": clean_text(raw.get("job_type") or raw.get("employment_type")),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
