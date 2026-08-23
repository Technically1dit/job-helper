from backend.app.config import settings
from backend.app.services import serpapi
from ..normalizer import normalize_job


class SerpApiProvider:
    name = "serpapi"

    @property
    def enabled(self):
        return bool(settings.SERPAPI_API_KEY)

    async def search(self, query: str, location: str, limit: int) -> list[dict]:
        if not self.enabled:
            return []
        raw_jobs = await serpapi.search_jobs(query, location)
        return [job for item in raw_jobs[:limit] if (job := normalize_job(item, self.name))]
