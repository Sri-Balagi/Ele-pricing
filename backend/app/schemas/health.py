from typing import Any, List
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
    engine_reports: List[Any] = Field(default_factory=list)

class SystemPipelineResponse(BaseModel):
    """Pipeline diagnostic info."""
    registered_engines: List[str]
    catalogue_version: str
    schema_version: str
    startup_timestamp: str
    uptime_seconds: float
    ready: bool
