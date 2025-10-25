# app/routers/ml_router.py
from fastapi import APIRouter, HTTPException
from app.services import ml_service
from app.schemas.ml_schema import PredictionRequest, PredictionResponse

router = APIRouter(
    prefix="/api",
    tags=["Machine Learning"]
)

@router.post("/predict", response_model=PredictionResponse)
def predict_match_outcome(request: PredictionRequest):
    """
    Internal endpoint to get a match prediction.
    Takes a JSON object of match features and returns win probabilities.
    """
    try:
        # --- IMPORTANT ---
        # This list MUST be in the same order as the columns
        # in your model's ColumnTransformer.
        features = [
            request.batting_team,
            request.bowling_team,
            request.city,
            request.runs_left,
            request.ball_left,
            request.wickets_remaining,
            request.total_runs_x,
            request.crr,
            request.rrr
        ]
        
        # Get the prediction from our service
        result = ml_service.get_match_prediction(features)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")