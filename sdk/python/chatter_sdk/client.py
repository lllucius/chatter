"""
Mock Chatter client for testing.
"""

from typing import Optional

import aiohttp

from .models import HealthResponse


class ChatterClient:
    """Mock Chatter API client."""

    def __init__(self, base_url: str = "http://localhost:8000", access_token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None:
            headers = {}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"

            self._session = aiohttp.ClientSession(base_url=self.base_url, headers=headers)
        return self._session

    async def health_check(self) -> HealthResponse:
        """Perform health check."""
        session = await self._get_session()

        async with session.get("/api/v1/health") as response:
            data = await response.json()
            return HealthResponse(**data)

    async def close(self) -> None:
        """Close the client session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
