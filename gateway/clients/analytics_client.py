import httpx
from fastapi import HTTPException


class AnalyticsClient:
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url
        self.timeout = timeout

    async def get_top_tags(self, limit: int = 5, min_confidence: float = 30.0):
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {"limit": limit, "min_confidence": min_confidence}
                response = await client.get(f"{self.base_url}/top-tags/", params=params)

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code, detail=response.text
                    )

                return response.json()

        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Analytics service timeout")
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Analytics service unavailable")

    async def get_stats(self):
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/stats/")

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code, detail=response.text
                    )

                return response.json()

        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Analytics service timeout")
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Analytics service unavailable")
