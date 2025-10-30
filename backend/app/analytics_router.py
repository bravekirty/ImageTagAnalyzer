import logging

from fastapi import APIRouter, HTTPException
from sqlalchemy import distinct, func, select

from app.database import async_session_maker
from app.models import ImageTag, Image
from app.utils import *


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/analytics",
    tags=["Аналитика"],
)


@router.get("/top-tags/")
async def get_top_tags_analytics(limit: int = 5, min_confidence: float = 30.0):
    async with async_session_maker() as session:
        try:
            total_images_result = await session.execute(select(func.count(Image.id)))
            total_images = total_images_result.scalar() or 1

            total_tags_result = await session.execute(select(func.count(ImageTag.id)))
            total_tags = total_tags_result.scalar() or 0

            avg_tags_per_image = total_tags / total_images if total_images > 0 else 0
            stmt = (
                select(
                    ImageTag.tag_name,
                    func.count(ImageTag.id).label("occurrence_count"),
                    func.avg(ImageTag.confidence).label("avg_confidence"),
                    func.count(distinct(ImageTag.image_id)).label("image_count"),
                )
                .where(ImageTag.confidence >= min_confidence)
                .group_by(ImageTag.tag_name)
                .order_by(func.count(ImageTag.id).desc())
                .limit(limit)
            )

            result = await session.execute(stmt)
            tag_analytics = result.all()

            analytics_result = []
            for (
                tag_name,
                occurrence_count,
                avg_confidence,
                image_count,
            ) in tag_analytics:
                percentage_on_images = (
                    (image_count / total_images * 100) if total_images > 0 else 0
                )

                analytics_result.append(
                    {
                        "tag_name": tag_name,
                        "occurrence_count": occurrence_count,
                        "image_count": image_count,
                        "percentage_on_images": round(percentage_on_images, 2),
                        "avg_confidence": (
                            round(avg_confidence, 2) if avg_confidence else 0
                        ),
                    }
                )

            return {
                "total_images": total_images,
                "avg_tags_per_image": round(avg_tags_per_image, 2),
                "min_confidence": min_confidence,
                "top_tags": analytics_result,
            }

        except Exception as e:
            logger.error(f"Error generating analytics: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/")
async def get_overall_stats():
    async with async_session_maker() as session:
        try:
            total_images_result = await session.execute(select(func.count(Image.id)))
            total_images = total_images_result.scalar() or 0

            total_tags_result = await session.execute(select(func.count(ImageTag.id)))
            total_tags = total_tags_result.scalar() or 0

            avg_tags_per_image = total_tags / total_images if total_images > 0 else 0

            most_common_stmt = (
                select(ImageTag.tag_name, func.count(ImageTag.id).label("count"))
                .group_by(ImageTag.tag_name)
                .order_by(func.count(ImageTag.id).desc())
            )
            most_common_result = await session.execute(most_common_stmt)
            most_common_tag = most_common_result.first()

            highest_confidence_stmt = (
                select(
                    ImageTag.tag_name,
                    func.avg(ImageTag.confidence).label("avg_confidence"),
                )
                .group_by(ImageTag.tag_name)
                .order_by(func.avg(ImageTag.confidence).desc())
            )
            highest_confidence_result = await session.execute(highest_confidence_stmt)
            highest_confidence_tag = highest_confidence_result.first()

            return {
                "total_images": total_images,
                "total_tags": total_tags,
                "avg_tags_per_image": round(avg_tags_per_image, 2),
                "most_common_tag": {
                    "name": most_common_tag[0] if most_common_tag else None,
                    "count": most_common_tag[1] if most_common_tag else 0,
                },
                "highest_confidence_tag": {
                    "name": (
                        highest_confidence_tag[0] if highest_confidence_tag else None
                    ),
                    "avg_confidence": (
                        round(highest_confidence_tag[1], 2)
                        if highest_confidence_tag
                        else 0
                    ),
                },
            }

        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
