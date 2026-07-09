"""
Catalogue endpoints — read-only access to product catalogue data.

These endpoints expose the in-memory catalogue loaded at startup.
No business logic — pure data queries.
"""

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_pipeline
from app.services.configuration_pipeline import ConfigurationPipeline
from app.schemas.api.v1.responses import APISuccessEnvelope
from datetime import datetime, timezone

router = APIRouter(tags=["Catalogue"])


def _envelope(data) -> APISuccessEnvelope:
    return APISuccessEnvelope(
        success=True,
        data=data,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get(
    "/categories",
    response_model=APISuccessEnvelope,
    summary="List elevator categories",
    description="Returns all active elevator categories available for selection.",
)
async def list_categories(pipeline: ConfigurationPipeline = Depends(get_pipeline)):
    cats = [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "active": c.active,
            "metadata": c.metadata,
        }
        for c in pipeline.catalogue.categories
        if c.active
    ]
    return _envelope(cats)


@router.get(
    "/features",
    response_model=APISuccessEnvelope,
    summary="List features",
    description="Returns all configurable features grouped by their feature group.",
)
async def list_features(pipeline: ConfigurationPipeline = Depends(get_pipeline)):
    features = [
        {
            "id": f.id,
            "name": f.name,
            "description": f.description,
            "group_id": f.group_id,
            "category_id": f.category_id,
            "required": f.required,
            "active": f.active,
        }
        for f in pipeline.catalogue.features
        if f.active and f.configurable
    ]
    return _envelope(features)


@router.get(
    "/feature-options",
    response_model=APISuccessEnvelope,
    summary="List feature options",
    description="Returns all selectable feature options. Each option belongs to a feature.",
)
async def list_feature_options(pipeline: ConfigurationPipeline = Depends(get_pipeline)):
    options = [
        {
            "id": o.id,
            "feature_id": o.feature_id,
            "display_name": o.display_name,
            "description": o.description,
            "active": o.active,
        }
        for o in pipeline.catalogue.feature_options
        if o.active
    ]
    return _envelope(options)
