#!/bin/bash

echo "Running database migrations..."
alembic upgrade head

echo "Loading sample images..."
python -c "
import asyncio
from app.sample_images_router import load_sample_images

asyncio.run(load_sample_images())
"

echo "All setup tasks completed!"

exec "$@"