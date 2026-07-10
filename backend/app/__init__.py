"""
Application package — exposes the create_app() factory.

create_app() is the single entry point for instantiating the FastAPI app.
It is used by:
  - main.py (production server)
  - tests/conftest.py (test client)

This separation enables the test suite to create isolated app instances
without starting a real server.
"""

import logging
from datetime import UTC

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.exceptions import ElevatorBaseException
from app.core.logging_config import setup_logging
from app.core.startup import build_lifespan
from app.middleware.request_logging import RequestLoggingMiddleware

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Create, configure, and return the FastAPI application instance.

    Steps:
      1. Load settings.
      2. Initialise logging.
      3. Build the FastAPI app with lifespan hooks.
      4. Register middleware (outermost first).
      5. Register global exception handlers.
      6. Mount API routers.

    Returns:
        Fully configured FastAPI application.
    """
    settings = get_settings()

    # Step 2: Logging must be set up before anything that logs
    setup_logging(
        log_level=settings.LOG_LEVEL,
        log_dir=settings.LOG_DIR,
        max_bytes=settings.LOG_MAX_BYTES,
        backup_count=settings.LOG_BACKUP_COUNT,
    )

    # Step 3: Create the app with lifecycle management
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Rule-Based Elevator Configuration and Pricing Engine (CPQ). "
            "Configures elevators, validates engineering constraints, "
            "resolves component dependencies, and calculates dynamic pricing."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=build_lifespan(data_dir=settings.DATA_DIR),
    )

    from app.middleware.timing import RequestTimingMiddleware

    # Step 4: Middleware — order matters (outermost registered last with add_middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestTimingMiddleware)

    # Step 5: Global exception handlers
    _register_exception_handlers(app)

    # Step 6: API routers
    app.include_router(v1_router, prefix=settings.API_V1_PREFIX)

    logger.info(
        "App created: %s v%s [%s] | API prefix: %s",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.ENVIRONMENT,
        settings.API_V1_PREFIX,
    )

    return app


def _get_request_metadata(request: Request) -> dict:
    from datetime import datetime, timezone

    # Prefer an explicitly passed correlation ID in headers or state
    corr_id = getattr(
        request.state, "correlation_id", request.headers.get("X-Correlation-ID")
    )
    return {
        "correlation_id": corr_id,
        "timestamp": datetime.now(UTC).isoformat(),
    }


def _register_exception_handlers(app: FastAPI) -> None:
    """
    Register centralized exception handlers on the FastAPI app.

    All application exceptions are converted to ErrorResponse JSON payloads.
    Raw Python exceptions never reach the client.
    """

    @app.exception_handler(ElevatorBaseException)
    async def elevator_exception_handler(
        request: Request,
        exc: ElevatorBaseException,
    ) -> JSONResponse:
        logger.error(
            "Application exception [%s]: %s | path=%s",
            exc.error_code,
            exc.message,
            request.url.path,
            extra={"details": exc.details},
        )
        meta = _get_request_metadata(request)
        return JSONResponse(
            status_code=exc.http_status,
            content={
                "success": False,
                "error_code": exc.error_code,
                "message": exc.message,
                "correlation_id": meta["correlation_id"],
                "timestamp": meta["timestamp"],
                "details": exc.details,
            },
        )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: object) -> JSONResponse:
        meta = _get_request_metadata(request)
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error_code": "NOT_FOUND",
                "message": f"Route '{request.url.path}' does not exist.",
                "correlation_id": meta["correlation_id"],
                "timestamp": meta["timestamp"],
                "details": None,
            },
        )

    @app.exception_handler(422)
    async def validation_error_handler(request: Request, exc: object) -> JSONResponse:
        details = exc.errors() if hasattr(exc, "errors") else str(exc)
        meta = _get_request_metadata(request)
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": "Request validation failed. Check 'details' for field errors.",
                "correlation_id": meta["correlation_id"],
                "timestamp": meta["timestamp"],
                "details": details,
            },
        )
