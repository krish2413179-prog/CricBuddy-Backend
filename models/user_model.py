from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base 

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    
   
    hashed_password = Column(String, nullable=True) 

    google_id = Column(String, unique=True, index=True, nullable=True)


    fcm_device_token = Column(String, nullable=True)