from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.core.database import Base

class UserFavoriteTeam(Base):
    __tablename__ = "user_favorite_teams"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))

    __table_args__ = (UniqueConstraint('user_id', 'team_id', name='_user_team_uc'),)