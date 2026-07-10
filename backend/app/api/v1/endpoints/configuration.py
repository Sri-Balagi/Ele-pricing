"""
Configuration CRUD and pipeline orchestration endpoints.
All existing contracts preserved. Additive: search endpoint, project_name, status reset on edit.
"""
import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response, Request

from app.api.v1.dependencies import get_pipeline, get_store
from app.core.constants import ConfigurationStatus
from app.models.domain import Configuration
from app.schemas.api.v1.requests import CreateConfigurationRequest, UpdateConfigurationRequest
from app.schemas.api.v1.responses import APISuccessEnvelope
from app.services.configuration_pipeline import ConfigurationPipeline
from app.services.store import BaseConfigurationStore

router = APIRouter(tags=["Configuration"])

# Statuses that get reset when a customer edits a saved configuration
_EDIT_RESETS_STATUS = {
    ConfigurationStatus.VALIDATED,
    ConfigurationStatus.PRICED,
    ConfigurationStatus.QUOTED,
    ConfigurationStatus.EXPORTED,
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _create_success_envelope(data, correlation_id: str = None) -> APISuccessEnvelope:
    return APISuccessEnvelope(
        success=True,
        data=data,
        correlation_id=correlation_id,
        timestamp=_now(),
    )


# ── SEARCH (must be before /{id} to avoid routing conflict) ──────────────────

@router.get(
    "/search",
    response_model=APISuccessEnvelope,
    summary="Search configurations",
    description="Case-insensitive search by project name, display ID, or configuration ID.",
)
async def search_configurations(
    q: str = Query("", description="Search term"),
    limit: int = Query(20, ge=1, le=100),
    store: BaseConfigurationStore = Depends(get_store),
):
    if hasattr(store, "search_async"):
        results = await store.search_async(q, limit=limit)
    else:
        # Fallback for InMemoryStore — basic linear scan
        configs = store.list(limit=1000, offset=0)
        ql = q.strip().lower()
        results = [
            {"display_id": i + 1, "configuration_id": c.configuration_id,
             "project_name": c.project_name or "", "status": c.status,
             "selected_category": c.selected_category or "", "pricing_total": None}
            for i, c in enumerate(configs)
            if ql in (c.project_name or "").lower() or ql in c.configuration_id.lower()
        ][:limit]
    return _create_success_envelope(results)


# ── CREATE ────────────────────────────────────────────────────────────────────

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
        project_name=request_data.project_name,
        status=ConfigurationStatus.CONFIGURED,
        selected_category=request_data.selected_category or "",
        selected_feature_options=[],
        created_at=_now(),
    )
    try:
        if hasattr(store, "create_async"):
            await store.create_async(new_config)
        else:
            store.create(new_config)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    return _create_success_envelope(new_config)


# ── LIST ──────────────────────────────────────────────────────────────────────

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
    if hasattr(store, "list_async"):
        rows = await store.list_async(limit=limit, offset=offset)
        # Return lightweight list (not full config blobs)
        items = [
            {
                "display_id": r["display_id"],
                "configuration_id": r["configuration_id"],
                "project_name": r["project_name"],
                "status": r["status"],
                "selected_category": r["selected_category"],
                "pricing_total": r["pricing_total"],
                "created_at": r["created_at"],
                "updated_at": r["updated_at"],
            }
            for r in rows
        ]
    else:
        configs = store.list(limit=limit, offset=offset)
        items = [c.model_dump() for c in configs]
    return _create_success_envelope(items)


# ── GET ───────────────────────────────────────────────────────────────────────

@router.get(
    "/{configuration_id}",
    response_model=APISuccessEnvelope,
    summary="Get configuration",
)
async def get_configuration(
    configuration_id: str,
    store: BaseConfigurationStore = Depends(get_store),
):
    if hasattr(store, "get_async"):
        config = await store.get_async(configuration_id)
    else:
        config = store.get(configuration_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return _create_success_envelope(config)


# ── UPDATE ────────────────────────────────────────────────────────────────────

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
    if hasattr(store, "get_async"):
        config = await store.get_async(configuration_id)
    else:
        config = store.get(configuration_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    if request_data.project_name is not None:
        config.project_name = request_data.project_name
    if request_data.selected_category is not None:
        config.selected_category = request_data.selected_category
    if request_data.selected_feature_options is not None:
        config.selected_feature_options = request_data.selected_feature_options

    # Auto-reset status to CONFIGURED when customer edits a completed config
    current = config.status.value if hasattr(config.status, "value") else str(config.status)
    if current in {s.value for s in _EDIT_RESETS_STATUS}:
        config.status = ConfigurationStatus.CONFIGURED

    try:
        if hasattr(store, "update_async"):
            await store.update_async(config)
        else:
            store.update(config)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
    return _create_success_envelope(config)


# ── VALIDATE / PIPELINE ───────────────────────────────────────────────────────

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
    if hasattr(store, "get_async"):
        config = await store.get_async(configuration_id)
    else:
        config = store.get(configuration_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    report = pipeline.execute(config)

    if hasattr(store, "update_async"):
        await store.update_async(config)
    else:
        store.update(config)
    return _create_success_envelope(report, correlation_id=report.correlation_id)


# ── PRICING ───────────────────────────────────────────────────────────────────

@router.get(
    "/{configuration_id}/pricing",
    response_model=APISuccessEnvelope,
    summary="Get pricing summary",
)
async def get_configuration_pricing(
    configuration_id: str,
    store: BaseConfigurationStore = Depends(get_store),
):
    if hasattr(store, "get_async"):
        config = await store.get_async(configuration_id)
    else:
        config = store.get(configuration_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    if not config.pricing_summary:
        raise HTTPException(status_code=404, detail="Pricing summary not available yet. Run validate first.")

    # Promote status
    if config.status not in (ConfigurationStatus.QUOTED, ConfigurationStatus.EXPORTED):
        config.status = ConfigurationStatus.PRICED
        if hasattr(store, "update_async"):
            await store.update_async(config)
        else:
            store.update(config)

    return _create_success_envelope(config.pricing_summary)


# ── VALIDATION RESULTS ────────────────────────────────────────────────────────

@router.get(
    "/{configuration_id}/validation",
    response_model=APISuccessEnvelope,
    summary="Get validation results",
)
async def get_configuration_validation(
    configuration_id: str,
    store: BaseConfigurationStore = Depends(get_store),
):
    if hasattr(store, "get_async"):
        config = await store.get_async(configuration_id)
    else:
        config = store.get(configuration_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return _create_success_envelope({"status": config.status, "validation_results": config.validation_results})


# ── BOM ───────────────────────────────────────────────────────────────────────

@router.get(
    "/{configuration_id}/bom",
    response_model=APISuccessEnvelope,
    summary="Get bill of materials",
)
async def get_configuration_bom(
    configuration_id: str,
    store: BaseConfigurationStore = Depends(get_store),
):
    if hasattr(store, "get_async"):
        config = await store.get_async(configuration_id)
    else:
        config = store.get(configuration_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    if not config.bill_of_materials:
        raise HTTPException(status_code=404, detail="BOM not available yet. Run validate first.")
    
    return _create_success_envelope(config.bill_of_materials.model_dump())


# ── DELETE ────────────────────────────────────────────────────────────────────

@router.delete(
    "/{configuration_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete configuration",
)
async def delete_configuration(
    configuration_id: str,
    store: BaseConfigurationStore = Depends(get_store),
):
    if hasattr(store, "delete_async"):
        deleted = await store.delete_async(configuration_id)
    else:
        deleted = store.delete(configuration_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
