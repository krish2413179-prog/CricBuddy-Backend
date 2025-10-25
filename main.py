from fastapi import FastAPI
from contextlib import asynccontextmanager # <-- IMPORT THIS
from apscheduler.schedulers.asyncio import AsyncIOScheduler # <-- IMPORT THIS

from app.core.database import engine
from app.models import user_model
from app.routers import auth_router, match_router, user_router, ml_router, websocket_router, webhook_router

# --- IMPORT YOUR NEW MODULES ---
from app.core import firebase # This will run the init code
from app.services import notification_service


# --- DEFINE THE LIFESPAN EVENT HANDLER ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Code to run ON STARTUP ---
    print("Server starting up...")
    
    # 1. Initialize Firebase (by importing it)
    _ = firebase
    
    # 2. Initialize and start the scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        notification_service.check_for_upcoming_matches,
        trigger="interval",
        minutes=5  # Run this job every 5 minutes
    )
    scheduler.start()
    
    yield # This is the point where the app is "running"
    
    # --- Code to run ON SHUTDOWN ---
    print("Server shutting down...")
    scheduler.shutdown()

# ---------------------------------------------

user_model.Base.metadata.create_all(bind=engine)

# --- PASS THE LIFESPAN TO THE APP ---
app = FastAPI(lifespan=lifespan)

# --- Include all your routers ---
app.include_router(auth_router.router)
app.include_router(match_router.router)
app.include_router(user_router.router)
app.include_router(ml_router.router)
app.include_router(websocket_router.router)
app.include_router(webhook_router.router)

@app.get("/")
def read_root():
    return {"message": "Cricket App Backend v1"}