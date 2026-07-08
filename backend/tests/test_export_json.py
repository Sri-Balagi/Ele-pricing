import json
import pytest
from app.export.json_exporter import JSONExporter
from app.models.domain import ExportContext
from app.core.constants import ExportFormat

def test_json_export_structure_and_schema(sample_configuration):
    exporter = JSONExporter()
    context = ExportContext(
        configuration=sample_configuration,
        correlation_id="test-123",
        execution_timestamp="2026-07-08T00:00:00Z",
        export_format=ExportFormat.JSON
    )
    
    report = exporter.export(context)
    assert report.success
    assert report.content is not None
    assert report.export_format == ExportFormat.JSON
    
    data = json.loads(report.content.decode('utf-8'))
    assert data["schema_version"] == "1.0"
    assert "configuration" in data
    assert "export_metadata" in data
    assert "checksum" in data["export_metadata"]
    assert report.checksum is not None
