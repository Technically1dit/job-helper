import asyncio
import logging
from dataclasses import dataclass

from backend.app.config import settings
from .deduplicator import deduplicate
from .providers import ApifyProvider, JobSpyProvider, SerpApiProvider, WorkopiaProvider
from .ranking import filter_by_location

logger = logging.getLogger(__name__)


class JobSearchUnavailable(Exception):
    pass


@dataclass
class SearchOutcome:
    jobs: list[dict]
    sources: dict[str, int]


async def _run(provider, query: str, location: str, limit: int):
    try:
        jobs = await asyncio.wait_for(provider.search(query, location, limit), timeout=settings.JOB_SEARCH_TIMEOUT_SECONDS + 1)
        return provider.name, jobs, None
    except Exception as exc:
        logger.warning("Job provider %s failed: %s", provider.name, type(exc).__name__)
        return provider.name, [], exc


async def search_jobs(query: str, location: str) -> SearchOutcome:
    """Search primary providers concurrently and invoke SerpAPI as fallback."""
    limit = settings.JOB_SEARCH_RESULT_LIMIT
    primary = [provider for provider in (WorkopiaProvider(), JobSpyProvider(), ApifyProvider()) if provider.enabled]
    source_counts: dict[str, int] = {}
    raw_jobs: list[dict] = []
    failures = []
    if primary:
        for name, jobs, failure in await asyncio.gather(*[_run(p, query, location, limit) for p in primary]):
            source_counts[name] = len(jobs)
            raw_jobs.extend(jobs)
            if failure:
                failures.append(failure)
    # SerpAPI remains a fallback, and is used when the primary sources don't
    # supply enough jobs for a useful result set.
    serpapi_provider = SerpApiProvider()
    if len(raw_jobs) < min(10, limit) and serpapi_provider.enabled:
        name, jobs, failure = await _run(serpapi_provider, query, location, limit)
        source_counts[name] = len(jobs)
        raw_jobs.extend(jobs)
        if failure:
            failures.append(failure)
    if not raw_jobs and failures:
        raise JobSearchUnavailable()
    filtered = filter_by_location(deduplicate(raw_jobs), location)
    return SearchOutcome(jobs=filtered[:limit], sources=source_counts)
