import httpx
from sqlalchemy.orm import Session
from firebase_admin import messaging
from datetime import datetime, timedelta

from app.core.database import SessionLocal
from app.models.user_model import User
from app.models.favorite_model import UserFavoriteTeam
from app.models.team_model import Team

async def check_for_upcoming_matches():
    """
    This function is run by the scheduler.
    It checks for matches starting soon and sends notifications.
    """
    print(f"[{datetime.now()}] Running notification job...")
    
    # Background tasks need their own DB session
    db: Session = SessionLocal()
    
    try:
        # 1. Get upcoming matches from our *own* cached endpoint
        api_data = {}
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8000/api/schedule")
            if response.status_code != 200:
                print(f"Notification job failed: Could not get schedule. Status: {response.status_code}")
                return
            api_data = response.json()

        # --- ADAPT THIS ---
        # You must parse your Sports API's response structure
        matches = api_data.get("matches", []) 
        if not matches:
            print("No upcoming matches found.")
            return

        time_now = datetime.utcnow()
        notification_window = time_now + timedelta(minutes=15) # 15 min window

        for match in matches:
            # --- ADAPT THIS ---
            # You MUST correctly parse the start time string from your API
            match_start_time_str = match.get("start_time_utc") # Example key
            if not match_start_time_str:
                continue
                
            # Example parsing:
            match_start_time = datetime.fromisoformat(match_start_time_str.replace("Z", "+00:00"))

            # 2. Check if match is in our 15-minute window
            if time_now < match_start_time <= notification_window:
                team_a_id = match.get("team_a_id")
                team_b_id = match.get("team_b_id")
                
                # 3. Find all users who favorited these teams
                users_to_notify = db.query(User).join(UserFavoriteTeam).filter(
                    (UserFavoriteTeam.team_id == team_a_id) | (UserFavoriteTeam.team_id == team_b_id),
                    User.fcm_device_token != None # Only get users with a token
                ).distinct(User.id).all()
                
                if not users_to_notify:
                    continue

                # 4. Get their tokens
                tokens = [user.fcm_device_token for user in users_to_notify]
                
                # 5. Send the notification
                message_title = "Match Starting Soon!"
                message_body = f"{match.get('team_a_name')} vs {match.get('team_b_name')} is about to begin!"

                message = messaging.MulticastMessage(
                    notification=messaging.Notification(
                        title=message_title,
                        body=message_body
                    ),
                    tokens=tokens,
                )
                response = messaging.send_multicast(message)
                print(f"Sent notification for match {match.get('id')}. Success: {response.success_count}, Fail: {response.failure_count}")
    
    except Exception as e:
        print(f"Error in notification job: {e}")
    finally:
        db.close() # Always close the session