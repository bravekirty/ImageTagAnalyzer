import hashlib

from typing import List
from sqlalchemy import select

from app.database import async_session_maker
from sqlalchemy.orm import Session
from app.models import Image


def get_optimal_tags(
    tags_data: List[dict], confidence_threshold: float = 30.0
) -> List[dict]:
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


def calculate_image_hash(image_data: bytes) -> str:
    return hashlib.sha256(image_data).hexdigest()


async def check_duplicate_image(image_hash: str) -> bool:
    async with async_session_maker() as session:
        result = await session.execute(
            select(Image).where(Image.image_hash == image_hash)
        )
        existing_image = result.scalar_one_or_none()
        return existing_image is not None


async def get_similar_images(
    image_hash: str, session: Session, similarity_threshold: int = 5
) -> List[Image]:
    async with async_session_maker() as session:
        result = await session.execute(
            select(Image).where(Image.image_hash == image_hash)
        )
        existing_image = result.scalar_one_or_none()
        return [existing_image] if existing_image else []
