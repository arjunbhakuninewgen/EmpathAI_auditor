# backend/auth/routes.py
"""
Authentication API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from database.connection import get_db
from database import crud
from .password import hash_password, verify_password
from .jwt import create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


# --- Request/Response Models ---

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]


# --- Routes ---

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account (API endpoint).
    """
    # Check if email already exists
    existing_user = crud.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    password_hash = hash_password(user_data.password)
    user = crud.create_user(db, user_data.email, password_hash, user_data.name)
    
    # Generate token
    token = create_access_token(str(user.id), user.email)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name
        }
    }


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password.
    """
    user = crud.get_user_by_email(db, credentials.email)
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    token = create_access_token(str(user.id), user.email)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name
        }
    }


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current user info from JWT token.
    """
    return current_user
