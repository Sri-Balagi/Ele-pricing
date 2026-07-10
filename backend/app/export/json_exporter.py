import hashlib
import json
import time

from app.core.constants import ExportFormat
from app.export.base_exporter import BaseExporter
from app.models.domain import ExportContext, ExportMetadata, ExportReport


class JSONExporter(BaseExporter):
    """
    Exports the complete Configuration as a JSON payload.
    Ensures complete serializability of all models.
    """

    def export(self, context: ExportContext) -> ExportReport:
        t0 = time.perf_counter()

        # Serialize the configuration using Pydantic's built-in model_dump
        config_dict = context.configuration.model_dump(mode="json")

        # Add required schema_version at the root level for the JSON export
        export_payload = {"schema_version": "1.0", "configuration": config_dict}

        json_str = json.dumps(export_payload, separators=(",", ":"))
        content_bytes = json_str.encode("utf-8")

        checksum = hashlib.sha256(content_bytes).hexdigest()
        file_size = len(content_bytes)
        generation_time_ms = (time.perf_counter() - t0) * 1000

        # Generate Metadata for this specific export
        metadata = ExportMetadata(
            generated_at=context.execution_timestamp,
            generated_by="Elevator Configuration Engine",
            generator_version="1.0",
            export_duration_ms=generation_time_ms,
            export_format=ExportFormat.JSON,
            checksum=checksum,
            filename=f"{context.configuration.configuration_id}.json",
            mime_type="application/json",
            file_size=file_size,
        )

        # In a real app we might attach this metadata to the export output as well,
        # but the config itself is what we are exporting. We will also include it.
        export_payload["export_metadata"] = metadata.model_dump(mode="json")

        # Re-encode to include metadata in checksum/size
        json_str = json.dumps(export_payload, separators=(",", ":"))
        content_bytes = json_str.encode("utf-8")
        checksum = hashlib.sha256(content_bytes).hexdigest()
        file_size = len(content_bytes)

        return ExportReport(
            export_format=ExportFormat.JSON,
            filename=f"{context.configuration.configuration_id}.json",
            mime_type="application/json",
            checksum=checksum,
            file_size=file_size,
            generation_time_ms=generation_time_ms,
            success=True,
            content=content_bytes,
        )
