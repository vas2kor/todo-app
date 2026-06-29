"""
Notification service — handles SMS and email delivery.

SMS is sent via the Twilio Messages REST API using httpx (already a project
dependency) so no additional Twilio SDK is required.

Delivery behaviour is controlled by environment:
  - If Twilio credentials are configured → real SMS is sent.
  - If credentials are missing and app is NOT production → delivery is skipped
    and the caller falls back to returning code_for_testing in the API response.
  - If credentials are missing and app IS production → an error is raised so the
    misconfiguration is visible immediately rather than silently failing.
"""

import base64
import logging
from typing import NamedTuple

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

TWILIO_BASE_URL = "https://api.twilio.com/2010-04-01"
_PLACEHOLDER = {
    "",
    "replace-me",
    "your-twilio-account-sid",
    "your-twilio-auth-token",
    "your-twilio-from-number",
    "your-twilio-messaging-service-sid",
}


class DeliveryResult(NamedTuple):
    sent: bool          # True if the external API call succeeded
    error: str | None   # Non-None if something went wrong


class SMSService:
    """Sends one-time passcodes to phone numbers via Twilio."""

    @staticmethod
    def _clean(value: str | None) -> str:
        """Normalize env values so accidental spaces do not break checks/API calls."""
        return (value or "").strip()

    @staticmethod
    def _is_configured() -> bool:
        account_sid = SMSService._clean(settings.twilio_account_sid)
        auth_token = SMSService._clean(settings.twilio_auth_token)
        messaging_service_sid = SMSService._clean(settings.twilio_messaging_service_sid)
        from_number = SMSService._clean(settings.twilio_from_number)

        return (
            bool(account_sid)
            and account_sid not in _PLACEHOLDER
            and bool(auth_token)
            and auth_token not in _PLACEHOLDER
            and (
                (
                    bool(messaging_service_sid)
                    and messaging_service_sid not in _PLACEHOLDER
                )
                or (
                    bool(from_number)
                    and from_number not in _PLACEHOLDER
                )
            )
        )

    @staticmethod
    def _basic_auth_header() -> str:
        """Build the HTTP Basic Auth header expected by Twilio."""
        account_sid = SMSService._clean(settings.twilio_account_sid)
        auth_token = SMSService._clean(settings.twilio_auth_token)
        credentials = f"{account_sid}:{auth_token}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    @classmethod
    async def send_otp(cls, phone: str, code: str) -> DeliveryResult:
        """
        Send a 6-digit OTP to *phone* via Twilio.

        Returns a DeliveryResult indicating whether the SMS was sent.
        Raises RuntimeError in production when Twilio is not configured.
        """
        if not cls._is_configured():
            if settings.is_production:
                raise RuntimeError(
                    "Twilio credentials are not configured. "
                    "Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and either "
                    "TWILIO_MESSAGING_SERVICE_SID or TWILIO_FROM_NUMBER."
                )
            # Development / staging: log and skip — the router will return
            # code_for_testing so developers can still test the flow.
            logger.warning(
                "Twilio is not configured — OTP %s for %s was NOT sent via SMS. "
                "Using code_for_testing fallback.",
                code,
                phone,
            )
            return DeliveryResult(sent=False, error=None)

        account_sid = cls._clean(settings.twilio_account_sid)
        messaging_service_sid = cls._clean(settings.twilio_messaging_service_sid)
        from_number = cls._clean(settings.twilio_from_number)

        url = f"{TWILIO_BASE_URL}/Accounts/{account_sid}/Messages.json"
        body = f"Your FlowBoard verification code is {code}. It expires in 2 minutes."
        data = {
            "To": phone,
            "Body": body,
        }
        if messaging_service_sid and messaging_service_sid not in _PLACEHOLDER:
            data["MessagingServiceSid"] = messaging_service_sid
        else:
            data["From"] = from_number

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    url,
                    headers={
                        "Authorization": cls._basic_auth_header(),
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    data=data,
                )

                if response.status_code in (200, 201):
                    payload = response.json()
                    sid = payload.get("sid", "unknown")
                    message_status = payload.get("status", "unknown")
                    error_code = payload.get("error_code")
                    error_message = payload.get("error_message")

                    # Twilio can return HTTP 201 while the message is already marked failed.
                    if error_code or message_status in {"failed", "undelivered", "canceled"}:
                        detail = f"Twilio status={message_status}, code={error_code}, message={error_message or 'n/a'}, sid={sid}"
                        logger.error("SMS OTP failed immediately: %s", detail)
                        return DeliveryResult(sent=False, error=detail)

                    logger.info("SMS OTP queued by Twilio to %s — SID %s (status=%s)", phone, sid, message_status)
                    return DeliveryResult(sent=True, error=None)

                error_msg = response.json().get("message", response.text)
                logger.error("Twilio responded with %s: %s", response.status_code, error_msg)
                return DeliveryResult(sent=False, error=error_msg)

        except httpx.HTTPError as exc:
            logger.error("Failed to reach Twilio: %s", exc)
            return DeliveryResult(sent=False, error=str(exc))
