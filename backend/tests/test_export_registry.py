import pytest

from app.core.constants import ExportFormat
from app.export.factory import ExportFactory
from app.export.json_exporter import JSONExporter
from app.export.registry import ExporterRegistry


def test_registry_registration_and_retrieval():
    registry = ExporterRegistry()
    exporter = JSONExporter()
    registry.register(ExportFormat.JSON, exporter)

    retrieved = registry.get_exporter(ExportFormat.JSON)
    assert retrieved is exporter


def test_factory_resolution():
    registry = ExporterRegistry()
    registry.register(ExportFormat.JSON, JSONExporter())

    factory = ExportFactory(registry)
    exporter = factory.create(ExportFormat.JSON)
    assert isinstance(exporter, JSONExporter)


def test_registry_unsupported_format():
    registry = ExporterRegistry()
    with pytest.raises(ValueError):
        registry.get_exporter(ExportFormat.PDF)
