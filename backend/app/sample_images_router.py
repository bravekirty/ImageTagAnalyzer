import json

from fastapi import APIRouter, HTTPException
from sqlalchemy import insert, select

from app.models import SampleImage
from app.database import async_session_maker
from app.sample_images import SAMPLE_IMAGES
from app.redis_client import get_cached_data, set_cached_data

router = APIRouter(prefix="/sample-images", tags=["Sample Images"])


@router.get("/")
async def get_sample_images():
    cached = get_cached_data("sample_images_list")
    if cached:
        print("cached")
        return cached

    async with async_session_maker() as session:
        result = await session.execute(
            select(SampleImage)
            .where(SampleImage.is_active == True)
            .order_by(SampleImage.id)
        )
        samples = result.scalars().all()

        response_data = [
            {
                "id": sample.id,
                "filename": sample.filename,
                "image_url": (
                    f"http://localhost:8000{sample.image_url}"
                    if not sample.image_url.startswith("http")
                    else sample.image_url
                ),
                "description": sample.description,
                "tags_count": (
                    len(json.loads(sample.tags_json)) if sample.tags_json else 0
                ),
            }
            for sample in samples
        ]

        set_cached_data("sample_images_list", response_data)
        print("not cached")
        return response_data


@router.post("/{sample_id}/analyze")
async def analyze_sample_image(sample_id: int, confidence_threshold: float = 30.0):
    cache_key = f"sample_analysis_{sample_id}_{confidence_threshold}"
    cached = get_cached_data(cache_key)
    if cached:
        return cached

    async with async_session_maker() as session:
        result = await session.execute(
            select(SampleImage).where(SampleImage.id == sample_id)
        )
        sample = result.scalar_one_or_none()

        if not sample:
            raise HTTPException(status_code=404, detail="Sample image not found")

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
        set_cached_data(cache_key, response_data, expire=86400)
        return response_data


@router.post("/load")
async def load_sample_images():
    async with async_session_maker() as session:
        for sample_data in SAMPLE_IMAGES:
            existing = await session.execute(
                select(SampleImage).where(
                    SampleImage.filename == sample_data["filename"]
                )
            )
            if not existing.scalar_one_or_none():
                stmt = insert(SampleImage).values(**sample_data)
                await session.execute(stmt)

        await session.commit()
