import logging
from app.core.config import settings

def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    # 🔥 Remove ALL existing handlers (important)
    root_logger.handlers.clear()

    if settings.ENV == "local":
        # Local mode: just structured Json logging
        from pythonjsonlogger import jsonlogger
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter()
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(module)s %(funcName)s %(lineno)d %(message)s"
        )
        handler.setFormatter(formatter)
    else:
        # Cloud mode: send directly to Cloud Logging
        from google.cloud.logging.handlers import StructuredLogHandler
        handler = StructuredLogHandler()

    root_logger.addHandler(handler)
    # 🔥 Fix duplication from uvicorn
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True