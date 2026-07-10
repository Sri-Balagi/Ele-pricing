from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from app.models.domain import (
    BillOfMaterials,
    ConfigurationStatus,
    PipelineExecutionReport,
    PricingSummary,
    ValidationResult,
)

T = TypeVar("T")


class APISuccessEnvelope(BaseModel, Generic[T]):
    """Standardized API Success Response Envelope."""

    success: bool = Field(default=True)
    data: T
    correlation_id: str | None = None
    timestamp: str


class ConfigurationResponse(BaseModel):
    """Payload returning the public state of a configuration."""

    configuration_id: str
    status: ConfigurationStatus
    customer_reference: str | None
    selected_category: str | None
    selected_feature_options: list[str]
    resolved_components: list[str]
    created_at: str | None
    expires_at: str | None


class ValidationResponse(BaseModel):
    """Payload returning the result of a validation run."""

    configuration_id: str
    status: ConfigurationStatus
    validation_results: ValidationResult


class PricingResponse(BaseModel):
    """Payload returning the result of a pricing run."""

    configuration_id: str
    status: ConfigurationStatus
    pricing_summary: PricingSummary
    bill_of_materials: BillOfMaterials


class PipelineResponse(BaseModel):
    """Payload returning the execution report from the orchestration layer."""

    correlation_id: str
    configuration_id: str
    success: bool
    status: ConfigurationStatus
    report: PipelineExecutionReport
