from fastapi import APIRouter

from . import contact_routes

api_router = APIRouter()

api_router.include_router(
    contact_routes.router,
    prefix="/v1/contact",
    tags=["contact"],
)

