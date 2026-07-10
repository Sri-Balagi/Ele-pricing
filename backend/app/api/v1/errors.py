from typing import Any

from pydantic import BaseModel, Field


class APIErrorEnvelope(BaseModel):
    """Standardized API Error Response Envelope."""

    success: bool = Field(default=False)
    error_code: str
    message: str
    correlation_id: str | None = None
    timestamp: str
    details: Any | None = None
