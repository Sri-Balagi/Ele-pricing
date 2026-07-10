from pydantic import BaseModel, Field


class CreateConfigurationRequest(BaseModel):
    """Payload for starting a new configuration session."""
    project_name: str = Field(..., min_length=1, description="Customer-given project name (e.g. 'My Apartment')")
    selected_category: str | None = Field(default=None, description="The chosen ElevatorCategory ID")
    # kept for backward compat
    customer_reference: str | None = Field(default=None, description="Deprecated: Optional CRM/ERP reference ID")


class UpdateConfigurationRequest(BaseModel):
    """Payload for updating an existing configuration."""
    project_name: str | None = Field(default=None, description="Update project name")
    selected_feature_options: list[str] | None = Field(default=None, description="IDs of selected FeatureOptions")
    selected_category: str | None = Field(default=None, description="The chosen ElevatorCategory ID")
