import logging
import time

from fastapi import FastAPI, Request

from app.core.logging_config import setup_logging
from app.models.models import Base
from app.routers import admin
from app.routers import auth
from app.db.database import engine

logger = logging.getLogger(__name__)

app = FastAPI()
setup_logging()
Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(admin.router)


@app.get("/health")
def healthy():
    return {"status": "health is OK"}


setup_logging()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    logger.info(
        "request_started main.py",
        extra={
            "path": request.url.path,
            "method": request.method,
            "start_time": start_time,
        },
    )

    response = await call_next(request)

    duration = time.time() - start_time

    logger.info(
        "Request_Completed main.py",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
        },
    )

    return response
