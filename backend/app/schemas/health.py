"""
Health check response schemas.

Separate from base.py because health-check has rich domain-specific fields
that do not belong in a generic response wrapper.
"""

from pydantic import BaseModel, Field

from app.core.constants import HealthStatus


class DataFilesStatus(BaseModel):
    """Per-file initialization status for the health endpoint."""

    components: bool = Field(description="components.json loaded successfully.")
    features: bool = Field(description="features.json loaded successfully.")
    dependencies: bool = Field(description="dependencies.json loaded successfully.")
    rules: bool = Field(description="rules.json loaded successfully.")
    pricing: bool = Field(description="pricing.json loaded successfully.")


class HealthResponse(BaseModel):
    """
    Health check endpoint response.

    Provides enough information for:
      - Load balancer health probes (check 'status')
      - Ops dashboards (check 'uptime_seconds', 'data_initialized')
      - Debugging startup issues (check 'data_files')
    """

    status: HealthStatus = Field(
        description="Overall application health: healthy | degraded | unhealthy.",
    )
    version: str = Field(description="Application version string.")
    environment: str = Field(description="Runtime environment name.")
    uptime_seconds: float = Field(
        description="Seconds elapsed since the application started.",
    )
    data_initialized: bool = Field(
        description="True when all five JSON data files loaded successfully.",
    )
    data_files: DataFilesStatus = Field(
        description="Per-file initialization status breakdown.",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "environment": "development",
                "uptime_seconds": 42.5,
                "data_initialized": True,
                "data_files": {
                    "components": True,
                    "features": True,
                    "dependencies": True,
                    "rules": True,
                    "pricing": True,
                },
            }
        }
    }
