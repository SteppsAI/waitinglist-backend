import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.database.core import get_db
from src.limiter import limiter
from src.models.mail import WaitlistResponse, WaitlistSignup
from src.services.resend_mail_service import ResendServiceError
from src.services.waitinglist_service import process_waitlist_signup

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/subscribe",
    response_model=WaitlistResponse,
    status_code=status.HTTP_200_OK,
)  # 200 makes it easier for clients to handle success.
@limiter.limit("5/minute")
async def subscribe_waitlist(
    request: Request,
    payload: WaitlistSignup,
    db: AsyncSession = Depends(get_db),
) -> WaitlistResponse:
    try:
        return await process_waitlist_signup(payload, db)
    except ResendServiceError as exc:
        logger.error("Resend error while subscribing %s: %s", payload.email, exc)
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error while processing waitlist signup")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while subscribing. Please try again later.",
        ) from exc
