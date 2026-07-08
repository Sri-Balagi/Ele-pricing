from fastapi import Request

from app.services.configuration_pipeline import ConfigurationPipeline
from app.services.store import BaseConfigurationStore

def get_pipeline(request: Request) -> ConfigurationPipeline:
    """Extracts the ConfigurationPipeline from application state."""
    # We will inject the pipeline into app.state during lifespan startup
    return request.app.state.pipeline

def get_store(request: Request) -> BaseConfigurationStore:
    """Extracts the ConfigurationStore from application state."""
    return request.app.state.store
