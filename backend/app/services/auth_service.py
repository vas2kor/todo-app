import random
import string
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import OTP, User


class OTPService:
    OTP_TIMEOUT_SECONDS = 120

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    @staticmethod
    def generate_otp_code() -> str:
        """Generate a random 6-digit OTP."""
        return "".join(random.choices(string.digits, k=6))

    async def request_otp(self, email: str | None, phone: str | None) -> OTP:
        """Create a new OTP for signup."""
        code = self.generate_otp_code()
        otp = OTP(email=email, phone=phone, code=code)
        self.db.add(otp)
        await self.db.commit()
        await self.db.refresh(otp)
        return otp

    async def verify_otp(self, email: str | None, phone: str | None, code: str) -> tuple[bool, User | None]:
        """Verify OTP and create user if valid."""
        query = select(OTP).where(OTP.code == code)
        if email:
            query = query.where(OTP.email == email)
        elif phone:
            query = query.where(OTP.phone == phone)

        result = await self.db.execute(query.order_by(OTP.created_at.desc()).limit(1))
        otp = result.scalar_one_or_none()

        if not otp:
            return False, None

        elapsed = (datetime.utcnow() - otp.created_at).total_seconds()
        if elapsed > self.OTP_TIMEOUT_SECONDS:
            return False, None

        # Mark OTP as verified
        otp.verified_at = datetime.utcnow()
        await self.db.commit()

        # Check if user already exists
        user_query = select(User)
        if email:
            user_query = user_query.where(User.email == email)
        elif phone:
            user_query = user_query.where(User.phone == phone)

        result = await self.db.execute(user_query)
        user = result.scalar_one_or_none()

        # Create user if doesn't exist
        if not user:
            user = User(email=email, phone=phone, verified_at=datetime.utcnow())
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)

        return True, user


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_or_create_oauth_user(self, provider: str, provider_id: str, email: str | None = None) -> User:
        """Get or create a user from OAuth provider."""
        query = select(User).where(User.oauth_provider == provider, User.oauth_id == provider_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if user:
            return user

        # Create new OAuth user
        user = User(oauth_provider=provider, oauth_id=provider_id, email=email, verified_at=datetime.utcnow())
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_by_id(self, user_id: str) -> User | None:
        """Fetch user by ID."""
        return await self.db.get(User, user_id)
