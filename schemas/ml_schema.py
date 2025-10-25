
from pydantic import BaseModel

class PredictionRequest(BaseModel):
    batting_team: str
    bowling_team: str
    city: str
    runs_left: int
    ball_left: int
    wickets_remaining: int
    total_runs_x: int
    crr: float
    rrr: float

class PredictionResponse(BaseModel):
    team_a_win_prob: float
    team_b_win_prob: float