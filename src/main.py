import logging
import os
import sys
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.limiter import limiter
from src.routes import api_router
from src.services.resend_mail_service import ResendServiceError

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(levelname)s:%(name)s:%(message)s",
)
logger = logging.getLogger("waitinglist-backend")

HEALTH_CHECK_TTL = 30 * 60  # 30 minutes
last_health_check = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 WaitingList backend starting up")
    yield
    logger.info("🛑 WaitingList backend shutting down")


app = FastAPI(lifespan=lifespan, title="WaitingList API")
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}"},
    )


@app.exception_handler(ResendServiceError)
async def resend_exception_handler(request: Request, exc: ResendServiceError):
    logger.error(f"Resend error: {exc}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)},
    )


app.add_middleware(SlowAPIMiddleware)

secret_key = os.getenv("SESSION_SECRET", "change-me")
app.add_middleware(SessionMiddleware, secret_key=secret_key)

origins = [
    "http://localhost:3000",
    "https://waitinglist-total.vercel.app",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "WaitingList backend up and running"}


@app.get("/api/health")
async def health():
    global last_health_check  # noqa: PLW0603
    current_time = time.time()
    if current_time - last_health_check >= HEALTH_CHECK_TTL:
        last_health_check = current_time
        logger.info("Health check OK (fresh)")
        return {"message": "OK", "timestamp": current_time}

    time_remaining = HEALTH_CHECK_TTL - (current_time - last_health_check)
    return {"message": "OK (cached)", "time_remaining": int(time_remaining)}


@app.get("/debug/routes")
async def debug_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, "path"):
            routes.append(
                {
                    "path": route.path,
                    "methods": list(getattr(route, "methods", [])),
                    "name": getattr(route, "name", "Unknown"),
                }
            )
    return {"routes": routes, "total": len(routes)}


def start():
    logger.info("Starting WaitingList backend on port 8000")
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)

