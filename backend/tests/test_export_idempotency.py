import pytest
from app.export.json_exporter import JSONExporter
from app.models.domain import ExportContext
from app.core.constants import ExportFormat

from unittest.mock import patch

@patch('time.perf_counter', return_value=1.0)
def test_export_idempotency(mock_time, sample_configuration):
    exporter = JSONExporter()
    context1 = ExportContext(
        configuration=sample_configuration,
        correlation_id="test-123",
        execution_timestamp="2026-07-08T00:00:00Z",
        export_format=ExportFormat.JSON
    )
    
    report1 = exporter.export(context1)
    
    context2 = ExportContext(
        configuration=sample_configuration,
        correlation_id="test-123",
        execution_timestamp="2026-07-08T00:00:00Z",
        export_format=ExportFormat.JSON
    )
    
    report2 = exporter.export(context2)
    
    assert report1.checksum == report2.checksum
    assert report1.content == report2.content
    
def test_export_checksum_stability(sample_configuration):
    exporter = JSONExporter()
    context = ExportContext(
        configuration=sample_configuration,
        correlation_id="test-123",
        execution_timestamp="2026-07-08T00:00:00Z",
        export_format=ExportFormat.JSON
    )
    report = exporter.export(context)
    assert report.checksum is not None
    # Verify the checksum is actually a valid sha256
    import re
    assert re.match(r'^[a-fA-F0-9]{64}$', report.checksum)
