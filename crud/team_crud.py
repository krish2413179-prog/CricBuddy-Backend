# app/crud/team_crud.py
from sqlalchemy.orm import Session
from app.models.team_model import Team
from app.schemas.team_schema import TeamBase

def upsert_team(db: Session, team: TeamBase) -> Team:
    """
    Update a team if it exists, or insert it if it doesn't.
    """
    # Try to find the team by its ID (from the sports API)
    db_team = db.query(Team).filter(Team.id == team.id).first()
    
    if db_team:
        # Team exists, update its info
        db_team.name = team.name
        db_team.logo_url = team.logo_url
    else:
        
        db_team = Team(**team.model_dump())
        db.add(db_team)
        
    db.commit()
    db.refresh(db_team)
    return db_team