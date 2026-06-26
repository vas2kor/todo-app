import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.schemas_auth import OTPRequest, OTPVerify, UserResponse, AuthToken, OAuthCallbackRequest
from app.services.auth_service import OTPService, UserService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"
PLACEHOLDER_VALUES = {"", "replace-me", "replace-with-prod-client-id", "replace-with-prod-client-secret"}


def _validate_google_oauth_config() -> None:
    if settings.oauth_google_client_id in PLACEHOLDER_VALUES:
        raise HTTPException(status_code=500, detail="Google OAuth client ID is not configured")
    if settings.oauth_google_client_secret in PLACEHOLDER_VALUES:
        raise HTTPException(status_code=500, detail="Google OAuth client secret is not configured")
    if not settings.oauth_google_redirect_uri:
        raise HTTPException(status_code=500, detail="Google OAuth redirect URI is not configured")


@router.post("/otp/request")
async def request_otp(payload: OTPRequest, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    """Request an OTP for signup via email or phone."""
    service = OTPService(db)
    try:
        otp = await service.request_otp(payload.email, payload.phone)
    except ValueError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc

    # In production: send OTP via email/SMS
    response = {"message": "OTP sent"}
    if settings.expose_test_otp and not settings.is_production:
        response["code_for_testing"] = otp.code
    return response


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
async def google_login(request: Request) -> dict[str, str]:
    """Initiate Google OAuth flow and return provider URL to frontend."""
    _validate_google_oauth_config()

    state = secrets.token_urlsafe(32)
    request.session["google_oauth_state"] = state

    query = urlencode(
        {
            "client_id": settings.oauth_google_client_id,
            "redirect_uri": settings.oauth_google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
    )
    return {"oauth_url": f"{GOOGLE_AUTH_ENDPOINT}?{query}"}


@router.post("/google/callback")
async def google_callback(payload: OAuthCallbackRequest, request: Request, db: AsyncSession = Depends(get_db)) -> AuthToken:
    """Handle Google OAuth callback code exchange and login."""
    _validate_google_oauth_config()

    expected_state = request.session.pop("google_oauth_state", None)
    if not expected_state or payload.state != expected_state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    async with httpx.AsyncClient(timeout=15) as client:
        token_response = await client.post(
            GOOGLE_TOKEN_ENDPOINT,
            data={
                "code": payload.code,
                "client_id": settings.oauth_google_client_id,
                "client_secret": settings.oauth_google_client_secret,
                "redirect_uri": settings.oauth_google_redirect_uri,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if token_response.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to exchange Google authorization code")

        token_payload = token_response.json()
        access_token = token_payload.get("access_token")
        if not access_token:
            raise HTTPException(status_code=502, detail="Google token response missing access_token")

        userinfo_response = await client.get(
            GOOGLE_USERINFO_ENDPOINT,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if userinfo_response.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to fetch Google user profile")

    google_user = userinfo_response.json()
    provider_id = google_user.get("sub")
    email = google_user.get("email")
    if not provider_id:
        raise HTTPException(status_code=502, detail="Google user profile missing sub identifier")

    user_service = UserService(db)
    user = await user_service.get_or_create_oauth_user("google", provider_id, email=email)
    token = f"bearer_{user.id}"
    return AuthToken(access_token=token, user=UserResponse.model_validate(user))


@router.post("/facebook/callback")
async def facebook_callback(payload: OAuthCallbackRequest, db: AsyncSession = Depends(get_db)) -> AuthToken:
    """Handle Facebook OAuth callback."""
    user_service = UserService(db)
    user = await user_service.get_or_create_oauth_user("facebook", payload.code, email=None)
    token = f"bearer_{user.id}"
    return AuthToken(access_token=token, user=UserResponse.model_validate(user))


@router.post("/apple/callback")
async def apple_callback(payload: OAuthCallbackRequest, db: AsyncSession = Depends(get_db)) -> AuthToken:
    """Handle Apple OAuth callback."""
    user_service = UserService(db)
    user = await user_service.get_or_create_oauth_user("apple", payload.code, email=None)
    token = f"bearer_{user.id}"
    return AuthToken(access_token=token, user=UserResponse.model_validate(user))
