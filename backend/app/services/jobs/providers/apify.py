import httpx

from backend.app.config import settings
from ..normalizer import normalize_job


class ApifyProvider:
    name = "apify"

    @property
    def enabled(self):
        return bool(settings.APIFY_API_TOKEN and (settings.APIFY_LINKEDIN_ACTOR or settings.APIFY_INDEED_ACTOR))

    async def search(self, query: str, location: str, limit: int) -> list[dict]:
        if not self.enabled:
            return []
        # Actors are deliberately configured, never assumed: their input and
        # result schemas vary by actor. Standard Apify dataset output is used.
        actor = settings.APIFY_LINKEDIN_ACTOR or settings.APIFY_INDEED_ACTOR
        url = f"https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"
        payload = {"search": query, "location": location, "maxItems": limit}
        async with httpx.AsyncClient(timeout=settings.JOB_SEARCH_TIMEOUT_SECONDS) as client:
            response = await client.post(url, params={"token": settings.APIFY_API_TOKEN}, json=payload)
            response.raise_for_status()
        return [job for item in response.json()[:limit] if (job := normalize_job(item, self.name))]
