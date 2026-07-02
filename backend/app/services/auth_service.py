"""
Authentication service.
Handles user registration, login, and login logging.
"""

from datetime import datetime, timezone

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.models.logging_model import LoginLog
from app.models.user_model import User
from app.schemas.auth_schema import RegisterRequest, TokenResponse
from app.utils.hashing import hash_password, verify_password
from app.utils.token import create_access_token


def register_user(request: RegisterRequest, db: Session) -> User:
    """Register a new user after validating uniqueness of email and username."""

    # Check email uniqueness
    existing_email = db.query(User).filter(
        User.email == request.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email sudah terdaftar",
        )

    # Check username uniqueness
    existing_username = db.query(User).filter(
        User.username == request.username
    ).first()

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username sudah digunakan",
        )

    # Create new user
    new_user = User(
        username=request.username,
        email=request.email,
        full_name=request.full_name,
        hashed_password=hash_password(request.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def login_user(
    form_data: OAuth2PasswordRequestForm,
    db: Session
) -> TokenResponse:
    """Authenticate a user, return a JWT token, and log the login activity."""

    # Find user by username
    user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    # Validate password
    if not user or not verify_password(
        form_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun tidak aktif",
        )

    # Create JWT token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username
        }
    )

    # Log login activity to dedicated login_log table
    login_log = LoginLog(
        user_id=user.id,
        timestamp=datetime.now(timezone.utc),
    )

    db.add(login_log)
    db.commit()

    # Return token response
    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )