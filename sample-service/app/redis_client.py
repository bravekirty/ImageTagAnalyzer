import json
import logging
from redis.asyncio import Redis, ConnectionPool
from app.config import settings

logger = logging.getLogger(__name__)


redis_pool = ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True,
    retry_on_timeout=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    max_connections=20,
)

redis_client = Redis(connection_pool=redis_pool)


async def get_cached_data(key):
    try:
        data = await redis_client.get(key)
        return json.loads(data) if data else None
    except Exception as e:
        logger.warning(f"Redis connection failed for get: {e}")
        return None


async def set_cached_data(key, data, expire=3600):
    try:
        await redis_client.setex(key, expire, json.dumps(data))
    except Exception as e:
        logger.warning(f"Redis connection failed for set: {e}")


async def close_redis():
    await redis_client.close()
