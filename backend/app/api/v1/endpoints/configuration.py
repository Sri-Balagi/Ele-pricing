import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response

from app.api.v1.dependencies import get_pipeline, get_store
from app.core.constants import ConfigurationStatus
from app.models.domain import Configuration
from app.schemas.api.v1.requests import CreateConfigurationRequest, UpdateConfigurationRequest
from app.schemas.api.v1.responses import APISuccessEnvelope
from app.services.configuration_pipeline import ConfigurationPipeline
from app.services.store import BaseConfigurationStore

router = APIRouter(tags=["Configuration"])

def _create_success_envelope(data, correlation_id: str = None) -> APISuccessEnvelope:
    return APISuccessEnvelope(
        success=True,
        data=data,
        correlation_id=correlation_id,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@router.post(
    "",
    response_model=APISuccessEnvelope,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new configuration",
)
async def create_configuration(
    request_data: CreateConfigurationRequest,
    store: BaseConfigurationStore = Depends(get_store),
):
    new_config = Configuration(
        configuration_id=f"CFG-{uuid.uuid4().hex[:8].upper()}",
        status=ConfigurationStatus.DRAFT,
        selected_category=request_data.selected_category or "",
        selected_feature_options=[],
    )
    store.create(new_config)
    return _create_success_envelope(new_config)


@router.get(
    "",
    response_model=APISuccessEnvelope,
    summary="List configurations",
)
async def list_configurations(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    store: BaseConfigurationStore = Depends(get_store),
):
    configs = store.list(limit=limit, offset=offset)
    return _create_success_envelope(configs)


@router.get(
    "/{configuration_id}",
    response_model=APISuccessEnvelope,
    summary="Get configuration",
)
async def get_configuration(
    configuration_id: str,
    store: BaseConfigurationStore = Depends(get_store),
):
    config = store.get(configuration_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return _create_success_envelope(config)


@router.put(
    "/{configuration_id}",
    response_model=APISuccessEnvelope,
    summary="Update configuration",
)
async def update_configuration(
    configuration_id: str,
    request_data: UpdateConfigurationRequest,
    store: BaseConfigurationStore = Depends(get_store),
):
    config = store.get(configuration_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    if request_data.selected_category is not None:
        config.selected_category = request_data.selected_category
    if request_data.selected_feature_options is not None:
        config.selected_feature_options = request_data.selected_feature_options
        
    config.status = ConfigurationStatus.DRAFT
    store.update(config)
    return _create_success_envelope(config)


@router.post(
    "/{configuration_id}/validate",
    response_model=APISuccessEnvelope,
    summary="Run validation pipeline",
)
async def validate_configuration(
    configuration_id: str,
    pipeline: ConfigurationPipeline = Depends(get_pipeline),
    store: BaseConfigurationStore = Depends(get_store),
):
    config = store.get(configuration_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
        
    report = pipeline.execute(config)
    store.update(config)
    return _create_success_envelope(report, correlation_id=report.correlation_id)


@router.get(
    "/{configuration_id}/pricing",
    response_model=APISuccessEnvelope,
    summary="Get pricing summary",
)
async def get_configuration_pricing(
    configuration_id: str,
    store: BaseConfigurationStore = Depends(get_store),
):
    config = store.get(configuration_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    if not config.pricing_summary:
        raise HTTPException(status_code=404, detail="Pricing summary not available yet")
        
    return _create_success_envelope(config.pricing_summary)


@router.get(
    "/{configuration_id}/validation",
    response_model=APISuccessEnvelope,
    summary="Get validation results",
)
async def get_configuration_validation(
    configuration_id: str,
    store: BaseConfigurationStore = Depends(get_store),
):
    config = store.get(configuration_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # We return the configuration status or validation context. The pipeline stores reports on the PipelineExecutionReport.
    # The requirement is just to return read-only status. We can return the Configuration itself or a specific field.
    return _create_success_envelope({"status": config.status})


@router.delete(
    "/{configuration_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete configuration",
)
async def delete_configuration(
    configuration_id: str,
    store: BaseConfigurationStore = Depends(get_store),
):
    if not store.delete(configuration_id):
        raise HTTPException(status_code=404, detail="Configuration not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
