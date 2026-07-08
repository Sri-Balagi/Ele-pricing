from pydantic import BaseModel, Field


class CreateConfigurationRequest(BaseModel):
    """Payload for starting a new configuration session."""
    customer_reference: str | None = Field(default=None, description="Optional CRM/ERP reference ID")
    selected_category: str | None = Field(default=None, description="The chosen ElevatorCategory ID")


class UpdateConfigurationRequest(BaseModel):
    """Payload for updating an existing configuration."""
    selected_feature_options: list[str] | None = Field(default=None, description="IDs of selected FeatureOptions")
    selected_category: str | None = Field(default=None, description="The chosen ElevatorCategory ID")
