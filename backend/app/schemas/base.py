"""
Common API response schemas used across all endpoints.

Design principles:
  - Every endpoint returns either SuccessResponse or ErrorResponse.
  - Internal domain models are NEVER exposed directly through the API.
  - Consistent response shape allows clients to build generic error handlers.
"""

from typing import Any

from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    """
    Standard wrapper for successful API responses.

    Usage:
        return SuccessResponse(message="Component retrieved.", data=component_dict)
    """

    success: bool = Field(
        default=True,
        description="Always True for success responses.",
    )
    message: str = Field(description="Human-readable success message.")
    data: Any | None = Field(
        default=None,
        description="Response payload — may be a dict, list, or None.",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Component retrieved successfully.",
                "data": {"id": "C001", "name": "Standard Motor"},
            }
        }
    }


class ErrorResponse(BaseModel):
    """
    Standard wrapper for all error API responses.

    Clients should check 'success' first, then inspect 'error_code'
    programmatically and 'message' for human display.

    Usage (in exception handlers):
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(...).model_dump()
        )
    """

    success: bool = Field(
        default=False,
        description="Always False for error responses.",
    )
    error_code: str = Field(
        description="Machine-readable error code (e.g. INVALID_COMPONENT).",
    )
    message: str = Field(description="Human-readable error description.")
    details: Any | None = Field(
        default=None,
        description="Additional debugging context — may be None in production.",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": False,
                "error_code": "INVALID_COMPONENT",
                "message": "Component 'C999' does not exist in the catalogue.",
                "details": {"requested_id": "C999"},
            }
        }
    }
