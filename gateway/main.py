from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware

from clients.analyze_client import AnalyzeClient
from clients.analytics_client import AnalyticsClient
from clients.sample_client import SampleClient
import httpx

from middleware import LoggingMiddleware, RateLimitMiddleware
from config import settings

app = FastAPI(title="ImageTag Gateway", version="1.0")

FRONTEND_URL = settings.FRONTEND_URL

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window=60)


analyze_client = AnalyzeClient(settings.ANALYZE_SERVICE_URL)
analytics_client = AnalyticsClient(settings.ANALYTICS_SERVICE_URL)
sample_client = SampleClient(settings.SAMPLE_SERVICE_URL)


TIMEOUT = 30.0


@app.post("/analyze/")
async def upload_image(
    file: UploadFile = File(...),
    confidence_threshold: float = 30.0,
    language: str = "en",
):
    return await analyze_client.upload_image(file, confidence_threshold, language)


@app.get("/analyze/images/")
async def get_all_images():
    return await analyze_client.get_all_images()


@app.get("/analyze/images/{image_id}")
async def get_image(image_id: int):
    return await analyze_client.get_image(image_id)


@app.get("/analytics/top-tags/")
async def get_top_tags_analytics(
    limit: int = Query(5, ge=1, le=50),
    min_confidence: float = Query(30.0, ge=0.0, le=100.0),
):
    return await analytics_client.get_top_tags(limit, min_confidence)


@app.get("/analytics/stats/")
async def get_overall_stats():
    return await analytics_client.get_stats()


@app.get("/sample/")
async def get_sample_images():
    return await sample_client.get_samples()


@app.post("/sample/{sample_id}/analyze")
async def analyze_sample_image(
    sample_id: int, confidence_threshold: float = Query(30.0, ge=0.0, le=100.0)
):
    return await sample_client.analyze_sample(sample_id, confidence_threshold)


@app.get("/health")
async def health_check():
    services = {
        "analyze_service": settings.ANALYZE_SERVICE_URL,
        "analytics_service": settings.ANALYTICS_SERVICE_URL,
        "sample_service": settings.SAMPLE_SERVICE_URL,
    }

    status = {"gateway": "healthy", "services": {}}

    for service_name, service_url in services.items():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{service_url}/health")
                status["services"][service_name] = (
                    "healthy" if response.status_code == 200 else "unhealthy"
                )
        except:
            status["services"][service_name] = "unavailable"

    return status


@app.get("/")
async def root():
    return {
        "message": "ImageTag API Gateway",
        "version": "1.0",
        "endpoints": {
            "analyze": "/analyze/",
            "analytics": "/analytics/",
            "sample": "/sample/",
        },
    }
