"""Authentication endpoints for teacher access control"""

from fastapi import APIRouter, HTTPException, Depends, Request, Response
from pydantic import BaseModel
from app.config.settings import get_settings
from app.middleware.rate_limiting import limiter
import secrets
import time
from typing import Dict

# In-memory session storage - simple approach for 3-4 teachers
active_sessions: Dict[str, float] = {}
SESSION_DURATION = 24 * 60 * 60  # 24 hours in seconds

router = APIRouter(prefix="/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    """Login request model"""
    password: str


class LoginResponse(BaseModel):
    """Login response model"""
    success: bool
    message: str
    session_token: str = ""


def cleanup_expired_sessions():
    """Remove expired sessions"""
    current_time = time.time()
    expired_tokens = [
        token for token, created_at in active_sessions.items()
        if current_time - created_at > SESSION_DURATION
    ]
    for token in expired_tokens:
        del active_sessions[token]


def is_authenticated(request: Request) -> bool:
    """Check if request has valid session"""
    cleanup_expired_sessions()
    
    # Check for session token in Authorization header or cookies
    auth_header = request.headers.get("Authorization", "")
    session_token = ""
    
    if auth_header.startswith("Bearer "):
        session_token = auth_header[7:]  # Remove "Bearer " prefix
    else:
        # Fallback to cookies
        session_token = request.cookies.get("session_token", "")
    
    return session_token in active_sessions


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")  # Rate limit login attempts
async def login(request: Request, login_data: LoginRequest):
    """Authenticate teacher with shared password"""
    settings = get_settings()
    
    # Validate password
    if login_data.password != settings.auth_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )
    
    # Generate session token
    session_token = secrets.token_urlsafe(32)
    active_sessions[session_token] = time.time()
    
    return LoginResponse(
        success=True,
        message="Authentication successful",
        session_token=session_token
    )


@router.post("/logout")
async def logout(request: Request):
    """Logout and invalidate session"""
    # Get session token
    auth_header = request.headers.get("Authorization", "")
    session_token = ""
    
    if auth_header.startswith("Bearer "):
        session_token = auth_header[7:]
    else:
        session_token = request.cookies.get("session_token", "")
    
    # Remove session if exists
    if session_token in active_sessions:
        del active_sessions[session_token]
    
    return {"message": "Logged out successfully"}


@router.get("/verify")
async def verify_session(request: Request):
    """Verify if current session is valid"""
    if is_authenticated(request):
        return {"authenticated": True, "message": "Valid session"}
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )


# Dependency for protected routes
async def require_auth(request: Request):
    """Dependency to require authentication"""
    if not is_authenticated(request):
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    return True