import asyncio
import logging
import os
from typing import Any, Dict

import resend

logger = logging.getLogger(__name__)

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "WaitingList <no-reply@waitinglist.app>")
DEFAULT_PRODUCT_NAME = os.getenv("WAITINGLIST_PRODUCT_NAME", "WaitingList")

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY.strip()
else:
    logger.warning("RESEND_API_KEY is not configured; emails will fail.")


class ResendServiceError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code


def _build_email_body(name: str) -> tuple[str, str]:
    product_name = DEFAULT_PRODUCT_NAME
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #111;">
        <p>Hi {name},</p>
        <p>Thank you for joining our waitlist. We appreciate your interest in {product_name}.</p>
        <p>
          Our product turns any workflow into a clean, editable step-by-step guide in seconds.
          Simply record your process once, and our AI transforms it into comprehensive documentation
          that your team can actually use.
        </p>
        <p>
          We're excited to have you with us and look forward to sharing more as we get closer to our launch.
        </p>
        <p>Best regards,<br/>The Team</p>
      </body>
    </html>
    """

    text_body = (
        f"Hi {name},\n\n"
        "Thank you for joining our waitlist. We appreciate your interest in "
        f"{product_name}.\n\n"
        "Our product turns any workflow into a clean, editable step-by-step guide in seconds. "
        "Simply record your process once, and our AI transforms it into comprehensive documentation "
        "that your team can actually use.\n\n"
        "We're excited to have you with us and look forward to sharing more as we get closer to our launch.\n\n"
        "Best regards,\n"
        "The Team"
    )

    return html_body, text_body


async def send_waitlist_confirmation_email(name: str, email: str) -> Dict[str, Any]:
    if not RESEND_API_KEY:
        raise ResendServiceError("Email service is niet geconfigureerd.")

    safe_name = name.strip() or "there"
    html_body, text_body = _build_email_body(safe_name)
    product_name = DEFAULT_PRODUCT_NAME

    params = {
        "from": RESEND_FROM_EMAIL,
        "to": [email],
        "subject": f"Welcome to the {product_name} waitlist!",
        "html": html_body,
        "text": text_body,
    }

    logger.info("Sending waitlist confirmation email to %s for %s", email, product_name)

    try:
        response = await asyncio.to_thread(resend.Emails.send, params)
        logger.debug("Resend response: %s", response)
        return {
            "success": True,
            "message": "Confirmation email sent",
            "id": response.get("id"),
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to send waitlist confirmation email")
        raise ResendServiceError("Verzenden van de bevestigingsmail is mislukt.", status_code=502) from exc
