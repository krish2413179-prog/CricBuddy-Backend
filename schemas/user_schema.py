
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserPublic(UserBase):
    id: int

    class Config:
        orm_mode = True 
        
class FCMToken(BaseModel):
    fcm_token: str