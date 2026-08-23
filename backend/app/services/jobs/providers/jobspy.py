import asyncio
import logging

from backend.app.config import settings
from ..normalizer import normalize_job

logger = logging.getLogger(__name__)


class JobSpyProvider:
    """Optional scraper adapter, off by default on Vercel serverless."""
    name = "jobspy"

    @property
    def enabled(self):
        return settings.JOBSPY_ENABLED

    async def search(self, query: str, location: str, limit: int) -> list[dict]:
        if not self.enabled:
            return []
        try:
            return await asyncio.wait_for(asyncio.to_thread(self._search_sync, query, location, limit), timeout=settings.JOB_SEARCH_TIMEOUT_SECONDS)
        except ImportError:
            logger.warning("JobSpy enabled but python-jobspy is not installed")
            return []

    def _search_sync(self, query: str, location: str, limit: int) -> list[dict]:
        from jobspy import scrape_jobs
        frame = scrape_jobs(site_name=["indeed", "google"], search_term=query, location=location, results_wanted=limit)
        return [job for item in frame.to_dict("records") if (job := normalize_job(item, self.name))]
