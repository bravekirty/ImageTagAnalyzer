import os
import sys
import time
from sqlalchemy import create_engine, text


def wait_for_database(engine, max_retries=30):
    for i in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Database is ready!")
            return True
        except Exception as e:
            print(f"⏳ Database not ready yet (attempt {i+1}/{max_retries}): {e}")
            time.sleep(2)
    return False


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

        if not wait_for_database(engine):
            print("❌ Database never became ready")
            sys.exit(1)

        with engine.connect() as conn:
            from shared_models.database import Base
            from shared_models.models import Image, ImageTag, SampleImage

            print("📦 Creating tables...")
            Base.metadata.create_all(engine)
            print("✅ Database tables created successfully!")

            result = conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                )
            )
            tables = [row[0] for row in result]
            print(f"📊 Tables created: {tables}")

    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
