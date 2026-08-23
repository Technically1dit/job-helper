from __future__ import annotations


def filter_by_location(jobs: list[dict], requested_location: str) -> list[dict]:
    requested = requested_location.casefold().strip()
    if requested in {"remote", "anywhere"}:
        return [job for job in jobs if job.get("remote")]
    if requested in {"india", "india, remote"}:
        return jobs
    tokens = [token for token in requested.replace(",", " ").split() if len(token) > 2]
    return [job for job in jobs if job.get("remote") or any(token in (job.get("location") or "").casefold() for token in tokens)]


def score_job(job: dict, profile) -> tuple[int | None, dict | None]:
    """A deterministic, explainable score; no inferred candidate data."""
    if not profile or not profile.skills:
        return None, None
    haystack = f"{job.get('title', '')} {job.get('description', '')} {' '.join(job.get('skills') or [])}".casefold()
    candidate_skills = [str(skill).strip() for skill in profile.skills if str(skill).strip()]
    matching = [skill for skill in candidate_skills if skill.casefold() in haystack]
    if not matching:
        return 0, {"recommendation": "maybe", "matching_skills": [], "missing_skills": [], "short_summary": "No explicit profile skills were found in this listing."}
    score = round(100 * len(matching) / max(len(candidate_skills), 1))
    recommendation = "strong_apply" if score >= 70 else "apply" if score >= 40 else "maybe"
    return score, {"recommendation": recommendation, "matching_skills": matching, "missing_skills": [], "short_summary": f"Matches {len(matching)} skill{'s' if len(matching) != 1 else ''} listed in your profile."}
