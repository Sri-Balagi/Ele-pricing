import logging
import time

from fastapi import APIRouter, Depends, Request

from app.core.config import Settings, get_settings
from app.core.constants import HealthStatus
from app.schemas.health import (
    DetailedHealthResponse,
    ReadinessResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Health"])

_START_TIME: float = time.time()


@router.get(
    "/health",
    response_model=DetailedHealthResponse,
    summary="Health Diagnostics",
)
async def liveness_probe(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> DetailedHealthResponse:
    pipeline = getattr(request.app.state, "pipeline", None)

    pipeline_ready = False
    engine_reports = []

    if pipeline:
        try:
            startup_reports = pipeline.validate_startup()
            pipeline_ready = all(r.ready for r in startup_reports)
            engine_reports = [r.model_dump() for r in startup_reports]
        except Exception as e:
            logger.error("Detailed health check failed: %s", e)

    data_files = {
        "components": True,
        "features": True,
        "dependencies": True,
        "rules": True,
        "pricing": True,
    }

    return DetailedHealthResponse(
        status=HealthStatus.HEALTHY if pipeline_ready else HealthStatus.DEGRADED,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        uptime_seconds=round(time.time() - _START_TIME, 2),
        data_initialized=True,
        data_files=data_files,
        pipeline_ready=pipeline_ready,
        engine_reports=engine_reports,
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    summary="Readiness Probe",
)
async def readiness_probe(request: Request) -> ReadinessResponse:
    pipeline = getattr(request.app.state, "pipeline", None)

    if pipeline is None:
        return ReadinessResponse(status=HealthStatus.UNHEALTHY, ready=False)

    try:
        startup_reports = pipeline.validate_startup()
        ready = all(r.ready for r in startup_reports)
        return ReadinessResponse(
            status=HealthStatus.HEALTHY if ready else HealthStatus.DEGRADED,
            ready=ready,
        )
    except Exception as e:
        logger.error("Readiness check failed: %s", e)
        return ReadinessResponse(status=HealthStatus.UNHEALTHY, ready=False)
