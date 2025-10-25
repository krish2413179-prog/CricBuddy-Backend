# app/routers/auth_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.models.user_model import User
from app.schemas import user_schema, token_schema

router = APIRouter(
    prefix="/auth",  # All routes in this file will start with /auth
    tags=["Auth"]    # Groups them in the API docs
)

# --- 1. Email Registration Endpoint ---
@router.post("/register", response_model=user_schema.UserPublic)
def register_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password and create the new user
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

# --- 2. Email Login Endpoint ---
@router.post("/login", response_model=token_schema.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # Find the user by email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # Check if user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create and return a JWT token
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# --- 3. Google Sign-In Endpoint ---
@router.post("/google", response_model=token_schema.Token)
def auth_google(google_token: token_schema.GoogleToken, db: Session = Depends(get_db)):
    try:
        # Verify the token from Google
        idinfo = id_token.verify_oauth2_token(
            google_token.id_token, 
            google_requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )

        email = idinfo['email']
        google_id = idinfo['sub']

        # Check if user exists
        user = db.query(User).filter(User.google_id == google_id).first()

        if not user:
            # User doesn't exist, check if email is already used
            user = db.query(User).filter(User.email == email).first()
            if user:
                # Email exists (from email/pass login). Link the accounts.
                user.google_id = google_id
            else:
                # Brand new user. Create them.
                user = User(email=email, google_id=google_id)
                db.add(user)
            
            db.commit()
            db.refresh(user)
        
        # User exists, create and return a JWT token
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}

    except ValueError:
        # Invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google Token"
        ) 