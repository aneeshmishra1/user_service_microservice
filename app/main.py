import logging
import time

from fastapi import FastAPI, Request

from app.core.logging_config import setup_logging
from app.db.database import engine
from app.models.models import Base
from app.routers import auth

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(auth.router)


@app.on_event("startup")
async def startup_event():
    logger.info("user-service app ready and running")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("user-service app is shutting down")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Log request start
    logger.info(
        f"Request {request.url.path} started",
        extra={
            "path": request.url.path,
            "method": request.method,
            "start_time": start_time,
            "status_code": None,
            "duration_ms": None,
        },
    )

    response = await call_next(request)
    duration = time.time() - start_time

    # Log request completion
    logger.info(
        "Request completed",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "start_time": start_time,
        },
    )

    return response


@app.get("/health")
def healthy():
    return {"status": "health is OK"}
