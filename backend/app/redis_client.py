import redis
import json
from app.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    # password=settings.REDIS_PASSWORD,
    decode_responses=True,
)


def get_cached_data(key):
    data = redis_client.get(key)
    return json.loads(data) if data else None


def set_cached_data(key, data, expire=3600):
    redis_client.setex(key, expire, json.dumps(data))
