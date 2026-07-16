import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Path, Request
from fastapi.responses import Response

from app.core.constants import ConfigurationStatus, ExportFormat
from app.export.factory import ExportFactory
from app.models.domain import ExportContext
from app.services.store import BaseConfigurationStore

router = APIRouter()


@router.get("/{configuration_id}/export/{format_type}", summary="Export Configuration")
async def export_configuration(
    request: Request,
    configuration_id: str = Path(..., description="Configuration ID"),
    format_type: str = Path(..., description="json, pdf, excel"),
):
    """Generates a read-only export of the requested configuration."""
    store: BaseConfigurationStore = request.app.state.store
    export_factory: ExportFactory = request.app.state.export_factory

    config = store.get(configuration_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    if config.status not in [
        ConfigurationStatus.PRICED,
        ConfigurationStatus.QUOTED,
        ConfigurationStatus.EXPORTED,
    ]:
        raise HTTPException(
            status_code=400, detail="Only finalized configurations can be exported."
        )

    format_enum = None
    if format_type.lower() == "json":
        format_enum = ExportFormat.JSON
    elif format_type.lower() == "pdf":
        format_enum = ExportFormat.PDF
    elif format_type.lower() == "excel":
        format_enum = ExportFormat.EXCEL
    elif format_type.lower() == "zip":
        format_enum = ExportFormat.ZIP
    else:
        raise HTTPException(
            status_code=400, detail=f"Unsupported format: {format_type}"
        )

    exporter = export_factory.create(format_enum)

    correlation_id = request.headers.get("x-correlation-id", f"EXPORT-{uuid.uuid4()}")
    context = ExportContext(
        configuration=config,
        correlation_id=correlation_id,
        execution_timestamp=datetime.now(UTC).isoformat(),
        export_format=format_enum,
        catalogue=request.app.state.pipeline.catalogue
        if hasattr(request.app.state, "pipeline")
        else None,
    )

    report = exporter.export(context)

    if not report.success:
        raise HTTPException(status_code=500, detail="Export failed to generate.")

    if config.status != ConfigurationStatus.EXPORTED:
        config.status = ConfigurationStatus.EXPORTED
        if hasattr(store, "update_async"):
            await store.update_async(config)
        else:
            store.update(config)

    return Response(
        content=report.content,
        media_type=report.mime_type,
        headers={"Content-Disposition": f"attachment; filename={report.filename}"},
    )


@router.get("/{configuration_id}/quote", summary="Retrieve Quote Information")
async def get_quote_info(
    request: Request, configuration_id: str = Path(..., description="Configuration ID")
):
    """Retrieve quote metadata and summary (read-only)."""
    store: BaseConfigurationStore = request.app.state.store
    config = store.get(configuration_id)

    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    if not config.quote_metadata:
        raise HTTPException(
            status_code=400, detail="Quote not generated for this configuration."
        )

    if config.status not in [ConfigurationStatus.QUOTED, ConfigurationStatus.EXPORTED]:
        config.status = ConfigurationStatus.QUOTED
        if hasattr(store, "update_async"):
            await store.update_async(config)
        else:
            store.update(config)

    return {
        "configuration_id": config.configuration_id,
        "quote_metadata": config.quote_metadata.model_dump(),
        "pricing_summary": config.pricing_summary.model_dump()
        if config.pricing_summary
        else None,
    }
