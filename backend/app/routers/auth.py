from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas_auth import OTPRequest, OTPVerify, UserResponse, AuthToken
from app.services.auth_service import OTPService, UserService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/otp/request")
async def request_otp(payload: OTPRequest, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """Request an OTP for signup via email or phone."""
    service = OTPService(db)
    otp = await service.request_otp(payload.email, payload.phone)
    # In production: send OTP via email/SMS
    return {"message": "OTP sent", "code_for_testing": otp.code}


@router.post("/otp/verify")
async def verify_otp(payload: OTPVerify, db: AsyncSession = Depends(get_db)) -> AuthToken:
    """Verify OTP and create/return user."""
    service = OTPService(db)
    is_valid, user = await service.verify_otp(payload.email, payload.phone, payload.code)

    if not is_valid or not user:
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")

    # In production: generate JWT token here
    token = f"bearer_{user.id}"
    return AuthToken(access_token=token, user=UserResponse.model_validate(user))


@router.get("/google/login")
async def google_login() -> dict[str, str]:
    """Initiate Google OAuth flow (frontend will handle redirect)."""
    # In production: generate state, save to session, and return proper OAuth URL
    return {"oauth_url": "https://accounts.google.com/o/oauth2/v2/auth?..."}


@router.post("/google/callback")
async def google_callback(code: str, db: AsyncSession = Depends(get_db)) -> AuthToken:
    """Handle Google OAuth callback."""
    # In production: exchange code for token, fetch user info, create/get user
    user_service = UserService(db)
    user = await user_service.get_or_create_oauth_user("google", code, email=None)
    token = f"bearer_{user.id}"
    return AuthToken(access_token=token, user=UserResponse.model_validate(user))


@router.post("/facebook/callback")
async def facebook_callback(code: str, db: AsyncSession = Depends(get_db)) -> AuthToken:
    """Handle Facebook OAuth callback."""
    user_service = UserService(db)
    user = await user_service.get_or_create_oauth_user("facebook", code, email=None)
    token = f"bearer_{user.id}"
    return AuthToken(access_token=token, user=UserResponse.model_validate(user))


@router.post("/apple/callback")
async def apple_callback(code: str, db: AsyncSession = Depends(get_db)) -> AuthToken:
    """Handle Apple OAuth callback."""
    user_service = UserService(db)
    user = await user_service.get_or_create_oauth_user("apple", code, email=None)
    token = f"bearer_{user.id}"
    return AuthToken(access_token=token, user=UserResponse.model_validate(user))
