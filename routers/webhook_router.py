from fastapi import APIRouter, Request, HTTPException
from app.core.websocket_manager import manager
from app.services import ml_service

router = APIRouter(
    prefix="/api/webhooks",
    tags=["Webhooks"]
)

@router.post("/live-score")
async def receive_live_score(request: Request):
    """
    Receives live data from the external Sports API Webhook.
    Calculates ML prediction and broadcasts to all connected clients.
    """
    try:
        # 1. Get the live data from the webhook
        live_data = await request.json()
        
        # --- THIS IS AN EXAMPLE - YOU MUST ADAPT THIS ---
        # You need to parse the data your API sends.
        # Let's assume the webhook sends data like this:
        # {
        #   "match_id": 123,
        #   "batting_team": "Team A",
        #   "bowling_team": "Team B",
        #   "city": "Mumbai",
        #   "current_score": 100,
        #   "overs": 12.1,
        #   "wickets": 3,
        #   "target": 180,
        # }
        
        match_id = live_data["match_id"]
        
        # 2. Calculate features for your ML model
        # Again, this is an example calculation.
        total_runs_x = live_data["target"]
        runs_left = total_runs_x - live_data["current_score"]
        balls_bowled = int(live_data["overs"]) * 6 + (live_data["overs"] - int(live_data["overs"])) * 10
        ball_left = 120 - balls_bowled
        wickets_remaining = 10 - live_data["wickets"]
        crr = (live_data["current_score"] * 6) / balls_bowled if balls_bowled > 0 else 0
        rrr = (runs_left * 6) / ball_left if ball_left > 0 else 0

        # 3. Create the feature list in the *exact* order
        features = [
            live_data["batting_team"],
            live_data["bowling_team"],
            live_data["city"],
            runs_left,
            ball_left,
            wickets_remaining,
            total_runs_x,
            crr,
            rrr
        ]
        
        # 4. Get the ML prediction
        prediction = ml_service.get_match_prediction(features)
        
        # 5. Create the payload to send to the Flutter app
        payload = {
            "live_data": live_data,  # The raw data from the webhook
            "prediction": prediction # Your model's prediction
        }
        
        # 6. Broadcast to all clients watching this match
        await manager.broadcast_to_match(match_id, payload)
        
        return {"status": "success", "message": "Broadcasted live data"}

    except Exception as e:
        print(f"Webhook Error: {e}")
        raise HTTPException(status_code=500, detail="Error processing webhook")