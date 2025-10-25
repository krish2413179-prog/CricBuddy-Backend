# app/core/cache.py
import redis.asyncio as redis
from app.core.config import settings

redis_pool = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def get_redis():
    """
    Dependency to get a Redis connection from the pool.
    """
    async with redis_pool.pipeline(transaction=True) as pipe:
        yield pipe