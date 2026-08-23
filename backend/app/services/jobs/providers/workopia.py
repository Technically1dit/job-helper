import httpx

from backend.app.config import settings
from ..normalizer import normalize_job


class WorkopiaProvider:
    """Streamable-HTTP MCP adapter.

    Workopia requires OAuth/PKCE; this provider only runs when a user-scoped
    OAuth access token has been supplied by an approved integration. It does
    not substitute a REST request for MCP or attempt to bypass authentication.
    """
    name = "workopia"

    @property
    def enabled(self):
        return bool(settings.WORKOPIA_MCP_URL and settings.WORKOPIA_MCP_ACCESS_TOKEN)

    async def search(self, query: str, location: str, limit: int) -> list[dict]:
        if not self.enabled:
            return []
        headers = {
            "Authorization": f"Bearer {settings.WORKOPIA_MCP_ACCESS_TOKEN}",
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "MCP-Protocol-Version": "2025-03-26",
        }
        initialize = {
            "jsonrpc": "2.0", "id": 0, "method": "initialize",
            "params": {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "job-helper", "version": "1.0"}},
        }
        request = {
            "jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": "job_tool", "arguments": {"action": "search", "query": query, "location": location, "remote": location.casefold() == "remote", "limit": limit}},
        }
        async with httpx.AsyncClient(timeout=settings.JOB_SEARCH_TIMEOUT_SECONDS) as client:
            initialized = await client.post(settings.WORKOPIA_MCP_URL, headers=headers, json=initialize)
            initialized.raise_for_status()
            session_id = initialized.headers.get("Mcp-Session-Id")
            if session_id:
                headers["Mcp-Session-Id"] = session_id
            await client.post(settings.WORKOPIA_MCP_URL, headers=headers, json={"jsonrpc": "2.0", "method": "notifications/initialized"})
            response = await client.post(settings.WORKOPIA_MCP_URL, headers=headers, json=request)
            response.raise_for_status()
        return [job for item in self.parse_response(response.json())[:limit] if (job := normalize_job(item, self.name))]

    @staticmethod
    def parse_response(payload: dict) -> list[dict]:
        result = payload.get("result", payload)
        if isinstance(result, dict) and isinstance(result.get("jobs"), list):
            return result["jobs"]
        content = result.get("content", []) if isinstance(result, dict) else []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("json"), dict):
                return item["json"].get("jobs", [])
        return []
