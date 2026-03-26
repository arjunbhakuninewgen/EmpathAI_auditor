# backend/auth/jwt.py
"""
JWT Token handling for authentication.
"""
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "change-this-in-production-to-a-secure-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
REFRESH_WINDOW_HOURS = 72  # Accept expired tokens up to 72 hours old for silent refresh

security = HTTPBearer()


def create_access_token(user_id: str, email: str) -> str:
    """Create a JWT access token."""
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token_ignore_exp(token: str) -> Optional[dict]:
    """Decode a JWT token without validating expiry — for use in silent token refresh only."""
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_exp": False},
        )
        # Only allow refresh within REFRESH_WINDOW_HOURS after expiry
        exp = payload.get("exp")
        iat = payload.get("iat")
        if exp is None or iat is None:
            return None
        exp_dt = datetime.utcfromtimestamp(exp)
        if datetime.utcnow() > exp_dt + timedelta(hours=REFRESH_WINDOW_HOURS):
            return None  # too old to refresh
        return payload
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """FastAPI dependency to get current user from JWT token."""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return {
        "id": payload.get("sub"),
        "email": payload.get("email")
    }
