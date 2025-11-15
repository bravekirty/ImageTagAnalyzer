import os
import sys
from sqlalchemy import create_engine


def main():
    DB_HOST = os.getenv("DB_HOST", "db")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS", "postgres")
    DB_NAME = os.getenv("DB_NAME", "tag_analyzer")

    DATABASE_URL = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    print(f"🔄 Connecting to database: {DB_HOST}:{DB_PORT}/{DB_NAME}")

    try:
        engine = create_engine(DATABASE_URL)

        with engine.connect() as conn:
            from shared_models.database import Base
            from shared_models.models import Image, ImageTag, SampleImage

            print("📦 Creating tables...")
            Base.metadata.create_all(engine)
            print("✅ Database tables created successfully!")

    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
