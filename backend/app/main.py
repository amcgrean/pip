import logging
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.db.session import SessionLocal
from app.routes import api_router

app = FastAPI(title=settings.app_name)
logger = logging.getLogger("beisser_ops")

logging.basicConfig(
    level=getattr(logging, settings.log_level, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    started_at = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    logger.info(
        "request_completed method=%s path=%s status=%s duration_ms=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    logger.warning("validation_error count=%s", len(exc.errors()))
    return JSONResponse(status_code=422, content={"detail": "Invalid request payload", "errors": exc.errors()})


@app.on_event("startup")
def startup_checks():
    storage_root = Path(settings.local_storage_dir)
    storage_root.mkdir(parents=True, exist_ok=True)

    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        logger.exception("startup_db_connectivity_failed db=%s", settings.redacted_database_url)
        raise RuntimeError("Database connectivity check failed during startup") from exc

    logger.info(
        "startup_complete env=%s app_version=%s db=%s storage=%s",
        settings.environment,
        settings.app_version,
        settings.redacted_database_url,
        storage_root.resolve(),
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)
