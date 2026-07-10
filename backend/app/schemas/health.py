from typing import Any

from pydantic import BaseModel, Field

from app.core.constants import HealthStatus


class LivenessResponse(BaseModel):
    """Simple liveness probe."""

    status: HealthStatus = Field(default=HealthStatus.HEALTHY)
    uptime_seconds: float


class ReadinessResponse(BaseModel):
    """Simple readiness probe."""

    status: HealthStatus
    ready: bool


class DetailedHealthResponse(BaseModel):
    """Detailed diagnostics combining data and engine state."""

    status: HealthStatus
    version: str
    environment: str
    uptime_seconds: float
    data_initialized: bool
    data_files: dict[str, bool] = Field(default_factory=dict)
    pipeline_ready: bool
    engine_reports: list[Any] = Field(default_factory=list)


class StartupMetrics(BaseModel):
    application_startup_duration_ms: float
    repository_initialization_ms: float
    registry_initialization_ms: float
    pipeline_initialization_ms: float


class RuntimeMetrics(BaseModel):
    uptime_seconds: float
    total_requests_processed: int = 0
    pipeline_executions: int = 0


class SystemPipelineResponse(BaseModel):
    """Pipeline diagnostic info."""

    registered_engines: list[str]
    catalogue_version: str
    schema_version: str
    startup_timestamp: str
    ready: bool
    startup_metrics: StartupMetrics
    runtime_metrics: RuntimeMetrics
