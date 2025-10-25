# app/services/sports_api_service.py
import httpx
import json
from redis.asyncio import Pipeline
from sqlalchemy.orm import Session # <-- IMPORT THIS

from app.core.config import settings
from app.crud import team_crud # <-- IMPORT THIS
from app.schemas.team_schema import TeamBase # <-- IMPORT THIS

client = httpx.AsyncClient(...)

async def get_data_from_api(endpoint: str):
    ...

# --- UPDATE THIS FUNCTION ---
async def get_match_schedule(redis: Pipeline, db: Session): # <-- ADD db: Session
    """
    Fetches the match schedule.
    1. Tries cache.
    2. If not in cache, gets from API.
    3. Saves teams to our DB.
    4. Saves schedule to cache.
    """
    cache_key = "schedule:matches"
    
    cached_data = await redis.get(cache_key).execute()
    if cached_data[0]:
        print("Returning schedule from CACHE")
        return json.loads(cached_data[0])

    print("Returning schedule from API")
    api_data = await get_data_from_api(endpoint="/matches?status=upcoming") 

    if api_data:
        # --- ADD THIS LOGIC ---
        # Before caching, save the teams to our local DB
        # This is an EXAMPLE structure. You must adapt this to your
        # actual API provider's JSON response.
        try:
            for match in api_data.get("matches", []):
                if match.get("team_a"):
                    team_a = TeamBase(**match["team_a"]) # Assumes team_a is a dict
                    team_crud.upsert_team(db=db, team=team_a)
                if match.get("team_b"):
                    team_b = TeamBase(**match["team_b"]) # Assumes team_b is a dict
                    team_crud.upsert_team(db=db, team=team_b)
        except Exception as e:
            print(f"Error saving teams to DB: {e}")
        # ----------------------

        await redis.setex(cache_key, 3600, json.dumps(api_data)).execute()

    return api_data