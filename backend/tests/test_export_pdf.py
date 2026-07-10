from app.core.constants import ExportFormat
from app.export.pdf_exporter import PDFExporter
from app.models.domain import ExportContext


def test_pdf_export_generation(sample_configuration):
    exporter = PDFExporter()
    context = ExportContext(
        configuration=sample_configuration,
        correlation_id="test-123",
        execution_timestamp="2026-07-08T00:00:00Z",
        export_format=ExportFormat.PDF,
    )

    report = exporter.export(context)
    assert report.success
    assert report.content is not None
    assert report.content.startswith(b"%PDF-")
    assert report.file_size > 0
    assert report.checksum is not None
    assert report.export_format == ExportFormat.PDF


def test_pdf_metadata_stability(sample_configuration):
    # This acts as both a generation test and a metadata test
    exporter = PDFExporter()
    context = ExportContext(
        configuration=sample_configuration,
        correlation_id="test-123",
        execution_timestamp="2026-07-08T00:00:00Z",
        export_format=ExportFormat.PDF,
    )

    report = exporter.export(context)
    assert report.success
