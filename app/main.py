import logging
import time
import uuid

from fastapi import FastAPI, Request

from app.core.logging_config import setup_logging, request_id_ctx_var
from app.db.database import engine
from app.models.models import Base
from app.routers import auth

logger = logging.getLogger(__name__)

app = FastAPI()
setup_logging()
Base.metadata.create_all(bind=engine)
app.include_router(auth.router)

setup_logging()
logger = logging.getLogger("app.main")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    request_id = str(uuid.uuid4())  # Generate unique request ID
    request_id_ctx_var.set(request_id)  # Store in context for this request

    # Log request start
    logger.info(
        "Request started",
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
