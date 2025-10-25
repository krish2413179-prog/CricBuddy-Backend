from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.core.database import Base

class Match(Base):
    __tablename__ = "matches"

    
    
    id = Column(Integer, primary_key=True, index=True) 
  
    
    team_a_id = Column(Integer, ForeignKey("teams.id"))
    team_b_id = Column(Integer, ForeignKey("teams.id"))
    
    start_time = Column(DateTime)
    status = Column(String, default="Scheduled") 