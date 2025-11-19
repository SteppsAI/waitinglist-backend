import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.mail import WaitlistSignup, WaitlistResponse
from src.models.sqlalchemy_models import WaitingList
from src.services.resend_mail_service import send_waitlist_confirmation_email

logger = logging.getLogger(__name__)

async def process_waitlist_signup(
    payload: WaitlistSignup,
    db: AsyncSession
) -> WaitlistResponse:
    query = select(WaitingList).where(WaitingList.email_user == payload.email)
    existing = await db.execute(query)
    record = existing.scalar_one_or_none()

    if record:
        record.name_user = payload.name
        await db.commit()
        return WaitlistResponse(
            success=True,
            message="User already signed up!",
            is_existing=True
        )

    entry = WaitingList(name_user=payload.name, email_user=payload.email)
    db.add(entry)

    try:
        # Only persist the signup once the confirmation email is sent
        await send_waitlist_confirmation_email(
            name=payload.name,
            email=payload.email
        )
        await db.commit()
        await db.refresh(entry)
    except Exception:
        await db.rollback()
        raise

    return WaitlistResponse(
        success=True,
        message="Welcome to the waitlist! Keep your inbox in the loop.",
        is_existing=False
    )

