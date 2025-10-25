# app/routers/user_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.schemas.user_schema import TeamPublic, FCMToken

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user_model import User
from app.models.team_model import Team
from app.models.favorite_model import UserFavoriteTeam
from app.schemas.team_schema import TeamPublic

router = APIRouter(
    prefix="/api/me",       
    tags=["User"],
    dependencies=[Depends(get_current_user)]
)

class FavoriteRequest(BaseModel):
    team_id: int

# --- 1. GET MY FAVORITE TEAMS ---
@router.get("/favorites", response_model=List[TeamPublic])
def get_my_favorites(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Get a list of the current user's favorite teams.
    """
   
    favorite_teams = db.query(Team).join(UserFavoriteTeam).filter(
        UserFavoriteTeam.user_id == current_user.id
    ).all()
    
    return favorite_teams

@router.post("/favorites", status_code=status.HTTP_201_CREATED)
def add_favorite(
    favorite_req: FavoriteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    team_id = favorite_req.team_id
    
    
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Team not found"
        )
  
    existing_favorite = db.query(UserFavoriteTeam).filter(
        UserFavoriteTeam.user_id == current_user.id,
        UserFavoriteTeam.team_id == team_id
    ).first()
    
    if existing_favorite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team is already a favorite"
        )
        

    new_favorite = UserFavoriteTeam(user_id=current_user.id, team_id=team_id)
    db.add(new_favorite)
    db.commit()
    
    return {"message": "Favorite added successfully"}

# --- 3. REMOVE A FAVORITE TEAM ---
@router.delete("/favorites/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find the favorite entry
    favorite = db.query(UserFavoriteTeam).filter(
        UserFavoriteTeam.user_id == current_user.id,
        UserFavoriteTeam.team_id == team_id
    ).first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
        
    # Delete it
    db.delete(favorite)
    db.commit()
    
@router.post("/device-token")
def update_device_token(
    token_data: FCMToken,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Receives and updates the user's FCM device token.
    """
    current_user.fcm_device_token = token_data.fcm_token
    db.add(current_user)
    db.commit()
    return {"message": "FCM token updated successfully"}