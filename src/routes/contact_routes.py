import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.database.core import get_db
from src.limiter import limiter
from src.models.mail import WaitlistResponse, WaitlistSignup
from src.services.waitinglist_service import process_waitlist_signup

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/subscribe",
    response_model=WaitlistResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
async def subscribe_waitlist(
    request: Request,
    payload: WaitlistSignup,
    db: AsyncSession = Depends(get_db),
) -> WaitlistResponse:
    return await process_waitlist_signup(payload, db)
