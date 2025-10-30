import aiohttp
import logging

from datetime import datetime, timezone
from fastapi import APIRouter, File, UploadFile, HTTPException
from sqlalchemy import select

from app.database import async_session_maker
from app.models import ImageTag, Image
from app.utils import calculate_image_hash, check_duplicate_image, get_optimal_tags
from app.config import settings


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/image",
    tags=["Изображения"],
)


@router.post("/")
async def upload_image(
    file: UploadFile = File(..., description="Image file to process"),
    confidence_threshold: float = 30.0,
    language: str = "en",
):
    try:
        image_data = await file.read()

        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        image_hash = calculate_image_hash(image_data)
        is_duplicate = await check_duplicate_image(image_hash)
        if is_duplicate:
            raise HTTPException(
                status_code=409, detail="Duplicate image already exists"
            )

        params = {"language": language}

        async with aiohttp.ClientSession() as http_session:
            form_data = aiohttp.FormData()
            form_data.add_field(
                "image",
                image_data,
                filename=file.filename,
                content_type=file.content_type,
            )

            async with http_session.post(
                settings.IMAGGA_API_URL,
                auth=aiohttp.BasicAuth(
                    settings.IMAGGA_API_KEY, settings.IMAGGA_API_SECRET
                ),
                data=form_data,
                params=params,
                timeout=30,
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Imagga API error: {error_text}",
                    )

                imagga_data = await response.json()

        optimal_tags = get_optimal_tags(
            imagga_data["result"]["tags"], confidence_threshold
        )

        async with async_session_maker() as session:
            db_image = Image(
                filename=file.filename,
                original_filename=file.filename,
                file_size=len(image_data),
                mime_type=file.content_type,
                image_hash=image_hash,
                processed_date=datetime.now(timezone.utc),
            )

            session.add(db_image)
            await session.flush()

            for tag_data in optimal_tags:
                db_tag = ImageTag(
                    image_id=db_image.id,
                    tag_name=tag_data["tag_name"],
                    confidence=tag_data["confidence"],
                    language=language,
                    is_primary=tag_data["is_primary"],
                )
                session.add(db_tag)

            await session.commit()

            return {
                "image_id": db_image.id,
                "filename": file.filename,
                "total_tags": len(optimal_tags),
                "tags": optimal_tags,
                "primary_tags": [tag for tag in optimal_tags if tag["is_primary"]],
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images/")
async def get_all_images():
    async with async_session_maker() as session:
        try:
            result = await session.execute(select(Image))
            images = result.scalars().all()

            images_result = []
            for image in images:
                images_result.append(
                    {
                        "id": image.id,
                        "filename": image.filename,
                        "upload_date": image.upload_date,
                        "total_tags": len(image.tags),
                        "tags": [
                            {
                                "name": tag.tag_name,
                                "confidence": tag.confidence,
                                "is_primary": tag.is_primary,
                            }
                            for tag in image.tags
                        ],
                    }
                )

            return {"images": images_result}

        except Exception as e:
            logger.error(f"Error getting images: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/images/{image_id}")
async def get_image(image_id: int):
    async with async_session_maker() as session:
        try:
            result = await session.execute(select(Image).where(Image.id == image_id))
            image = result.scalar_one_or_none()

            if not image:
                raise HTTPException(status_code=404, detail="Image not found")

            return {
                "image": {
                    "id": image.id,
                    "filename": image.filename,
                    "upload_date": image.upload_date,
                    "file_size": image.file_size,
                    "mime_type": image.mime_type,
                },
                "tags": [
                    {
                        "name": tag.tag_name,
                        "confidence": tag.confidence,
                        "is_primary": tag.is_primary,
                    }
                    for tag in image.tags
                ],
            }

        except Exception as e:
            logger.error(f"Error getting image: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
