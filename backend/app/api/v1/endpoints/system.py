import logging
import time
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request

from app.api.v1.dependencies import get_pipeline, get_store
from app.schemas.health import RuntimeMetrics, StartupMetrics, SystemPipelineResponse
from app.services.configuration_pipeline import ConfigurationPipeline
from app.services.store import BaseConfigurationStore

logger = logging.getLogger(__name__)
router = APIRouter(tags=["System"])

# We'll share _START_TIME from health.py or just declare another module-level.
_START_TIME: float = time.time()
_STARTUP_TIMESTAMP: str = datetime.now(UTC).isoformat()


@router.get(
    "/pipeline",
    response_model=SystemPipelineResponse,
    summary="System Pipeline Diagnostics",
    description="Returns deep diagnostic information about the core configuration pipeline.",
)
async def system_pipeline(
    request: Request,
    pipeline: ConfigurationPipeline = Depends(get_pipeline),
) -> SystemPipelineResponse:

    startup_reports = pipeline.validate_startup()
    ready = all(r.ready for r in startup_reports)

    # Extract engine names
    engines = [r.engine_name for r in startup_reports]

    # Extract catalogue info
    metadata = pipeline.catalogue.metadata

    startup_metrics_dict = getattr(
        request.app.state,
        "startup_metrics",
        {
            "application_startup_duration_ms": 0.0,
            "repository_initialization_ms": 0.0,
            "registry_initialization_ms": 0.0,
            "pipeline_initialization_ms": 0.0,
        },
    )

    uptime = round(time.time() - _START_TIME, 2)
    # Mocking runtime metrics for now as they are not explicitly tracked globally yet
    # We will just expose uptime for runtime metrics

    return SystemPipelineResponse(
        registered_engines=engines,
        catalogue_version=metadata.catalogue_version,
        schema_version=metadata.schema_version,
        startup_timestamp=_STARTUP_TIMESTAMP,
        ready=ready,
        startup_metrics=StartupMetrics(**startup_metrics_dict),
        runtime_metrics=RuntimeMetrics(uptime_seconds=uptime),
    )


@router.get(
    "/store",
    summary="Store Diagnostics",
    description="Returns lightweight diagnostic information about the active configuration store.",
)
async def store_diagnostics(
    store: BaseConfigurationStore = Depends(get_store),
):
    # BaseConfigurationStore doesn't strictly have get_diagnostics defined in its ABC,
    # but since we know it's InMemoryConfigurationStore, we can call it.
    if hasattr(store, "get_diagnostics"):
        return store.get_diagnostics()
    return {"error": "Diagnostics not supported for this store type."}
