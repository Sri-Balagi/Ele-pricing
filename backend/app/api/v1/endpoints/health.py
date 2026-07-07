"""
Health check endpoint.

GET /api/v1/health

Returns application health, version, environment, uptime, and per-file
data initialization status.

Design notes:
  - No business logic here — this endpoint only reports infrastructure status.
  - DataLoader is instantiated per-request for validation (no side effects on cache).
  - _START_TIME is module-level so uptime is measured from import time,
    which closely approximates application startup time.
"""

import logging
import time

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.core.constants import DataFile, HealthStatus
from app.schemas.health import DataFilesStatus, HealthResponse
from app.utils.data_loader import DataLoader

logger = logging.getLogger(__name__)
router = APIRouter()

# Module-level: set when this module is first imported (application startup)
_START_TIME: float = time.time()


def _check_data_files(settings: Settings) -> tuple[bool, DataFilesStatus]:
    """
    Validate all data files and return overall + per-file status.

    Uses a fresh DataLoader (no cache side effects) to give an accurate
    real-time health picture rather than a stale cached status.

    Args:
        settings: Application settings (injected).

    Returns:
        Tuple of (all_ok: bool, DataFilesStatus).
    """
    loader = DataLoader(data_dir=settings.DATA_DIR)
    results = loader.validate_all()

    return (
        all(results.values()),
        DataFilesStatus(
            components=results.get(DataFile.COMPONENTS.value, False),
            features=results.get(DataFile.FEATURES.value, False),
            dependencies=results.get(DataFile.DEPENDENCIES.value, False),
            rules=results.get(DataFile.RULES.value, False),
            pricing=results.get(DataFile.PRICING.value, False),
        ),
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Application Health Check",
    description=(
        "Returns overall application health status, version, environment, "
        "uptime in seconds, and the initialization status of each JSON data file."
    ),
    tags=["Health"],
)
async def health_check(
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    """Application health check endpoint."""
    all_ok, data_files = _check_data_files(settings)
    uptime_seconds = round(time.time() - _START_TIME, 2)

    status = HealthStatus.HEALTHY if all_ok else HealthStatus.DEGRADED

    logger.debug("Health check: status=%s uptime=%.2fs", status.value, uptime_seconds)

    return HealthResponse(
        status=status,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        uptime_seconds=uptime_seconds,
        data_initialized=all_ok,
        data_files=data_files,
    )
