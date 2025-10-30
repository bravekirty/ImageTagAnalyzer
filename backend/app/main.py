from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.analytics_router import router as analytics_router
from app.images_router import router as images_router
from app.sample_images_router import router as sample_router

app = FastAPI(title="Image Tagging API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(analytics_router)
app.include_router(images_router)
app.include_router(sample_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return {
        "message": "Image Tagging API",
        "endpoints": {
            "upload_image": "POST image/upload/",
            "top_tags_analytics": "GET /analytics/top-tags/",
            "overall_stats": "GET /analytics/stats/",
            "list_images": "GET /images/",
            "get_image": "GET /images/{image_id}",
        },
    }
