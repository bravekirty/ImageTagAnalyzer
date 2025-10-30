from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
    Boolean,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    image_hash = Column(String(64), unique=True, nullable=False, index=True)
    upload_date = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    processed_date = Column(DateTime(timezone=True), nullable=True)

    tags = relationship(
        "ImageTag",
        back_populates="image",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<Image {self.filename} ({self.image_hash})>"


class ImageTag(Base):
    __tablename__ = "image_tags"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    tag_name = Column(String(255), nullable=False)
    confidence = Column(Float, nullable=False)
    language = Column(String(10), default="en")
    is_primary = Column(Boolean, default=False)

    __table_args__ = (UniqueConstraint("image_id", "tag_name", name="uq_image_tag"),)

    image = relationship("Image", back_populates="tags")

    def __repr__(self):
        return f"<Tag {self.tag_name} ({self.confidence}%)>"


class SampleImage(Base):
    __tablename__ = "sample_images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    image_url = Column(String(500), nullable=False)
    description = Column(String(300), nullable=True)
    tags_json = Column(Text, nullable=False)
    upload_date = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    is_active = Column(Boolean, default=True)
