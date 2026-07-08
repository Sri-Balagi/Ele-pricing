from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class APIErrorEnvelope(BaseModel):
    """Standardized API Error Response Envelope."""
    success: bool = Field(default=False)
    error_code: str
    message: str
    correlation_id: Optional[str] = None
    timestamp: str
    details: Optional[Any] = None
