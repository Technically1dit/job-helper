import httpx
from backend.app.config import settings

async def search_jobs(query: str, location: str):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_jobs",
        "q": query,
        "location": location,
        "hl": "en",
        "gl": "us",
        "api_key": settings.SERPAPI_API_KEY
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("jobs_results", [])

async def search_company_info(company_name: str):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": f"{company_name} company about",
        "api_key": settings.SERPAPI_API_KEY
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json().get("organic_results", [])

async def search_contact_info(company_name: str):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": f"{company_name} recruiter email OR HR email OR talent acquisition",
        "api_key": settings.SERPAPI_API_KEY
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json().get("organic_results", [])
