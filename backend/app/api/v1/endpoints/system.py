import logging
from datetime import datetime, timezone
import time

from fastapi import APIRouter, Depends, Request

from app.schemas.health import SystemPipelineResponse
from app.api.v1.dependencies import get_pipeline
from app.services.configuration_pipeline import ConfigurationPipeline

logger = logging.getLogger(__name__)
router = APIRouter(tags=["System"])

# We'll share _START_TIME from health.py or just declare another module-level.
_START_TIME: float = time.time()
_STARTUP_TIMESTAMP: str = datetime.now(timezone.utc).isoformat()

@router.get(
    "/pipeline",
    response_model=SystemPipelineResponse,
    summary="System Pipeline Diagnostics",
    description="Returns deep diagnostic information about the core configuration pipeline.",
)
async def system_pipeline(
    pipeline: ConfigurationPipeline = Depends(get_pipeline),
) -> SystemPipelineResponse:
    
    startup_reports = pipeline.validate_startup()
    ready = all(r.ready for r in startup_reports)
    
    # Extract engine names
    engines = [r.engine_name for r in startup_reports]
    
    # Extract catalogue info
    metadata = pipeline.catalogue.metadata
    
    return SystemPipelineResponse(
        registered_engines=engines,
        catalogue_version=metadata.catalogue_version,
        schema_version=metadata.schema_version,
        startup_timestamp=_STARTUP_TIMESTAMP,
        uptime_seconds=round(time.time() - _START_TIME, 2),
        ready=ready,
    )
