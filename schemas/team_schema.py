# app/schemas/team_schema.py
from pydantic import BaseModel

class TeamBase(BaseModel):
    id: int
    name: str
    logo_url: str | None = None

class TeamPublic(TeamBase):
    class Config:
        orm_mode = True