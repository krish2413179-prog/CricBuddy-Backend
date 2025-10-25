from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True) 
    name = Column(String, index=True)
    logo_url = Column(String, nullable=True)