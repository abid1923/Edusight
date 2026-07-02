"""
Authentication routes: register and login.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth_schema import RegisterRequest, TokenResponse
from app.schemas.user_schema import UserResponse
from app.services import auth_service
from app.utils.limiter import limiter

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("5/minute")
def register(request: Request, register_data: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account."""
    user = auth_service.register_user(register_data, db)
    return user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and receive a JWT access token."""

    return auth_service.login_user(
        form_data,
        db
    )