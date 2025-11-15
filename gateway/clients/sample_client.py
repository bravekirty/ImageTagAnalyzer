import httpx
from fastapi import HTTPException


class SampleClient:
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url
        self.timeout = timeout

    async def get_samples(self):
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/")

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code, detail=response.text
                    )

                return response.json()

        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Sample service timeout")
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Sample service unavailable")

    async def analyze_sample(self, sample_id: int, confidence_threshold: float = 30.0):
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {"confidence_threshold": confidence_threshold}
                response = await client.post(
                    f"{self.base_url}/{sample_id}/analyze", params=params
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code, detail=response.text
                    )

                return response.json()

        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Sample service timeout")
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Sample service unavailable")

    async def load_samples(self):
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/load")

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code, detail=response.text
                    )

                return response.json()

        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Sample service timeout")
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Sample service unavailable")
