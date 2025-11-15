import logging
import json
from fastapi import FastAPI, HTTPException
from sqlalchemy import insert, select, text
from sqlalchemy.exc import SQLAlchemyError

from shared_models.database import async_session_maker
from shared_models.models import SampleImage

from app.sample_images import SAMPLE_IMAGES
from app.redis_client import get_cached_data, set_cached_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sample Images Service", version="1.0.0")


@app.on_event("startup")
async def load_sample_images():
    try:
        async with async_session_maker() as session:
            await session.execute(text("TRUNCATE TABLE sample_images RESTART IDENTITY"))
            await session.commit()

            for sample_data in SAMPLE_IMAGES:
                query = insert(SampleImage).values(**sample_data)
                await session.execute(query)

            await session.commit()

            return {
                "message": f"Loaded {len(SAMPLE_IMAGES)} sample images successfully"
            }

    except SQLAlchemyError as e:
        logger.error(f"Database error in load_sample_images: {e}")
        raise HTTPException(status_code=500, detail="Database error during load")
    except Exception as e:
        logger.error(f"Unexpected error in load_sample_images: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/")
async def get_sample_images():
    try:
        cached = await get_cached_data("sample_images_list")
        if cached:
            return cached

        async with async_session_maker() as session:
            result = await session.execute(
                select(SampleImage)
                .where(SampleImage.is_active == True)
                .order_by(SampleImage.id)
            )
            samples = result.scalars().all()

            if not samples:
                return {"message": "No sample images found. Try loading samples first."}

            response_data = [
                {
                    "id": sample.id,
                    "filename": sample.filename,
                    "image_url": sample.image_url,
                    "description": sample.description,
                    "tags_count": (
                        len(json.loads(sample.tags_json)) if sample.tags_json else 0
                    ),
                }
                for sample in samples
            ]

            await set_cached_data("sample_images_list", response_data)
            return response_data

    except SQLAlchemyError as e:
        logger.error(f"Database error in get_sample_images: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error(f"Unexpected error in get_sample_images: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/{sample_id}/analyze")
async def analyze_sample_image(sample_id: int, confidence_threshold: float = 30.0):
    try:
        cache_key = f"sample_analysis_{sample_id}_{confidence_threshold}"
        cached = await get_cached_data(cache_key)
        if cached:
            return cached

        async with async_session_maker() as session:
            result = await session.execute(
                select(SampleImage).where(SampleImage.id == sample_id)
            )
            sample = result.scalar_one_or_none()

            if not sample:
                raise HTTPException(status_code=404, detail="Sample image not found")

            if not sample.tags_json:
                tags_data = []
            else:
                tags_data = json.loads(sample.tags_json)

            def get_optimal_tags(tags_data, confidence_threshold):
                filtered_tags = []
                for tag in tags_data:
                    confidence = tag.get("confidence", 0)
                    if confidence >= confidence_threshold:
                        filtered_tags.append(
                            {
                                "tag_name": tag["tag"]["en"],
                                "confidence": confidence,
                                "is_primary": confidence > 60.0,
                            }
                        )
                filtered_tags.sort(key=lambda x: x["confidence"], reverse=True)
                return filtered_tags

            optimal_tags = get_optimal_tags(tags_data, confidence_threshold)

            response_data = {
                "image_id": f"sample_{sample.id}",
                "filename": sample.filename,
                "total_tags": len(optimal_tags),
                "tags": optimal_tags,
                "primary_tags": [tag for tag in optimal_tags if tag["is_primary"]],
                "is_sample": True,
            }
            await set_cached_data(cache_key, response_data, expire=86400)
            return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_sample_image: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
async def health_check():
    try:
        async with async_session_maker() as session:
            await session.execute(select(1))

        try:
            await set_cached_data("health_check", "test", expire=10)
        except:
            logger.warning("Redis connection failed")

        return {
            "status": "healthy",
            "service": "sample-service",
            "database": "connected",
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "sample-service",
            "database": "disconnected",
            "error": str(e),
        }


@app.get("/info")
async def root():
    return {
        "message": "Sample Images Service",
        "endpoints": ["/", "/{id}/analyze", "/load", "/health"],
    }
