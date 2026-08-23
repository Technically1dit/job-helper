import httpx
import re
from backend.app.config import settings

def build_job_search_params(query: str, location: str):
    """Build a location-first Google Jobs query.

    Google Jobs treats its `location` argument as a search context, rather
    than a strict result filter. Repeating the requested place in the query
    makes the user's selection explicit and avoids leaking results from the
    provider's previous/default city.
    """
    clean_query = " ".join(query.split())
    clean_location = " ".join(location.split())
    location_lower = clean_location.lower()
    country = "in" if re.search(r"\b(india|ahmedabad|mumbai|delhi|bengaluru|bangalore|pune|hyderabad|chennai|kolkata)\b", location_lower) else "us"
    return {
        "engine": "google_jobs",
        "q": f"{clean_query} jobs in {clean_location}",
        "location": clean_location,
        "hl": "en",
        "gl": country,
        "api_key": settings.SERPAPI_API_KEY,
    }

async def search_jobs(query: str, location: str):
    url = "https://serpapi.com/search"
    params = build_job_search_params(query, location)
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
