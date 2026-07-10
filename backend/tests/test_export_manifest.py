import json
from datetime import datetime

import pytest

from app.core.constants import ExportFormat
from app.export.zip_exporter import ZIPExporter
from app.models.domain import ExportContext


def test_export_manifest(sample_configuration):
    exporter = ZIPExporter()

    from app.models.domain import QuoteMetadata, QuoteStatus

    sample_configuration.quote_metadata = QuoteMetadata(
        quote_number="QT-11111",
        quote_version=1,
        status=QuoteStatus.APPROVED,
        valid_until="2026-12-31T00:00:00Z",
        quote_hash="dummy_hash",
    )

    context = ExportContext(
        configuration=sample_configuration,
        correlation_id="MANIFEST-TEST",
        execution_timestamp="2026-07-08T00:00:00Z",
        export_format=ExportFormat.ZIP,
    )

    report = exporter.export(context)
    assert report.success is True

    import io
    import zipfile

    zip_buffer = io.BytesIO(report.content)
    with zipfile.ZipFile(zip_buffer, "r") as zf:
        # manifest exists
        assert "manifest.json" in zf.namelist()

        manifest_content = zf.read("manifest.json")
        manifest_data = json.loads(manifest_content.decode("utf-8"))

        # schema_version exists
        assert "schema_version" in manifest_data

        # export_version exists
        assert "export_version" in manifest_data

        # backend_version exists
        assert "backend_version" in manifest_data

        # checksum count matches exported files
        assert len(manifest_data["checksums"]) == len(manifest_data["exported_files"])

        # filenames match archive
        for file in manifest_data["exported_files"]:
            assert file in zf.namelist()

        # timestamps are valid ISO8601
        try:
            datetime.fromisoformat(
                manifest_data["generated_timestamp"].replace("Z", "+00:00")
            )
        except ValueError:
            pytest.fail("generated_timestamp is not valid ISO8601")
