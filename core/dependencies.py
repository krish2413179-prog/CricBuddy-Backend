# app/core/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.core import security, config
from app.core.database import get_db
from app.models.user_model import User
from app.schemas.token_schema import TokenData

# This tells FastAPI where to look for the token (in the "Authorization" header)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Decode the JWT
        payload = jwt.decode(
            token, 
            config.settings.SECRET_KEY, 
            algorithms=[config.settings.ALGORITHM]
        )
        
        # 2. Get the email ("subject") from the token
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
        token_data = TokenData(email=email)
        
    except JWTError:
        raise credentials_exception
    
    # 3. Find the user in the database
    user = db.query(User).filter(User.email == token_data.email).first()
    
    if user is None:
        raise credentials_exception
        
    
    return user