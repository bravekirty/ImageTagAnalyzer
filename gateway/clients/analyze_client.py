import httpx
from fastapi import HTTPException, UploadFile


class AnalyzeClient:
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url
        self.timeout = timeout

    async def upload_image(
        self, file: UploadFile, confidence_threshold: float = 30.0, language: str = "en"
    ):
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                files = {"file": (file.filename, await file.read(), file.content_type)}
                params = {
                    "confidence_threshold": confidence_threshold,
                    "language": language,
                }

                response = await client.post(
                    f"{self.base_url}/", files=files, params=params
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code, detail=response.text
                    )

                return response.json()

        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Analyze service timeout")
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Analyze service unavailable")

    async def get_all_images(self):
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/images/")

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code, detail=response.text
                    )

                return response.json()

        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Analyze service timeout")
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Analyze service unavailable")

    async def get_image(self, image_id: int):
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/images/{image_id}")

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code, detail=response.text
                    )

                return response.json()

        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Analyze service timeout")
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Analyze service unavailable")
