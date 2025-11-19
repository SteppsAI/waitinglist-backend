import asyncio
import logging
import os
from typing import Any, Dict

import resend
from resend.exceptions import ResendError

logger = logging.getLogger(__name__)

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
SUPPORT_EMAIL = os.getenv("RESEND_SUPPORT_EMAIL", "support@stepps.ai")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", f"Stepps <{SUPPORT_EMAIL}>")
BRAND_NAME = "stepps.ai"

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY.strip()
else:
    logger.warning("RESEND_API_KEY is not configured; emails will fail.")


class ResendServiceError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code


def _build_email_body(name: str) -> tuple[str, str]:
    brand_name = BRAND_NAME
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #111;">
        <p>Hi {name},</p>
        <p>Thanks for joining the {brand_name} waitlist.</p>
        <p>
          We help teams turn workflows into clear, editable step-by-step guides in seconds.
          Record your process once and our AI keeps your documentation up to date automatically.
        </p>
        <p>We'll keep you posted as soon as we ship new updates.</p>
        <p>— The {brand_name} team</p>
      </body>
    </html>
    """

    text_body = (
        f"Hi {name},\n\n"
        f"Thanks for joining the {brand_name} waitlist.\n\n"
        "We help teams turn workflows into clear, editable step-by-step guides in seconds. "
        "Record your process once and our AI keeps your documentation up to date automatically.\n\n"
        "We'll keep you posted as soon as we ship new updates.\n\n"
        f"— The {brand_name} team"
    )

    return html_body, text_body


async def send_waitlist_confirmation_email(name: str, email: str) -> Dict[str, Any]:
    if not RESEND_API_KEY:
        raise ResendServiceError("Email service is niet geconfigureerd.")

    safe_name = name.strip() or "there"
    html_body, text_body = _build_email_body(safe_name)
    brand_name = BRAND_NAME

    params = {
        "from": RESEND_FROM_EMAIL,
        "reply_to": SUPPORT_EMAIL,
        "to": [email],
        "subject": f"Welcome to the {brand_name} waitlist!",
        "html": html_body,
        "text": text_body,
    }

    logger.info("Sending waitlist confirmation email to %s from %s", email, RESEND_FROM_EMAIL)

    try:
        response = await asyncio.to_thread(resend.Emails.send, params)
        logger.debug("Resend response: %s", response)
        return {
            "success": True,
            "message": "Confirmation email sent",
            "id": response.get("id"),
        }
    except ResendError as exc:
        logger.error("Resend rejected the email send request: %s", exc)
        detail = getattr(exc, "message", str(exc))
        raise ResendServiceError(detail or "Resend sent an error back.", status_code=502) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to send waitlist confirmation email")
        raise ResendServiceError("Sending the confirmation email failed.", status_code=502) from exc
