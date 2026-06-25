from datetime import datetime

from pydantic import BaseModel, Field


class OTPRequest(BaseModel):
    email: str | None = Field(default=None, description="Email address for OTP")
    phone: str | None = Field(default=None, description="Phone number for OTP (E.164 format)")

    def __init__(self, **data):
        super().__init__(**data)
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided")


class OTPVerify(BaseModel):
    email: str | None = None
    phone: str | None = None
    code: str = Field(min_length=6, max_length=6, description="6-digit OTP")


class UserCreate(BaseModel):
    id: str
    email: str | None = None
    phone: str | None = None


class UserResponse(BaseModel):
    id: str
    email: str | None
    phone: str | None
    oauth_provider: str | None
    verified_at: datetime | None

    class Config:
        from_attributes = True


class OAuthCallbackRequest(BaseModel):
    code: str
    state: str | None = None
    provider: str


class AuthToken(BaseModel):
    access_token: str
    user: UserResponse
