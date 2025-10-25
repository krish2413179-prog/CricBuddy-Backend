# app/routers/match_router.py
from fastapi import APIRouter, Depends
from redis.asyncio import Pipeline

from app.services import sports_api_service
from app.core.cache import get_redis

router = APIRouter(
    prefix="/api",  # All routes here will start with /api
    tags=["Matches & Stats"]
)

@router.get("/schedule")
async def get_schedule(redis: Pipeline = Depends(get_redis)):
    """
    API endpoint to get the match schedule.
    This is what your Flutter app will call.
    """
    data = await sports_api_service.get_match_schedule(redis)
    return data

