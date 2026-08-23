from __future__ import annotations

from .normalizer import canonical_url


def _key(value: str | None) -> str:
    return "".join(char for char in (value or "").casefold() if char.isalnum())


def deduplicate(jobs: list[dict]) -> list[dict]:
    """Prefer canonical application/source URLs, then company-title-location."""
    seen: set[tuple[str, ...]] = set()
    unique: list[dict] = []
    for job in jobs:
        external_id = job.get("external_id")
        url = canonical_url(job.get("apply_url") or job.get("source_url"))
        identity = ("external", job.get("provider", ""), str(external_id)) if external_id else (("url", url) if url else ("fields", _key(job.get("company_name")), _key(job.get("title")), _key(job.get("location"))))
        if identity in seen:
            continue
        seen.add(identity)
        unique.append(job)
    return unique
