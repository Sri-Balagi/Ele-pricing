import time

import pytest

from app.core.constants import ExportFormat
from app.export.json_exporter import JSONExporter
from app.models.domain import (
    BillOfMaterials,
    BOMItem,
    BOMOrigin,
    Configuration,
    ExportContext,
)


def generate_large_configuration(num_components: int) -> Configuration:
    config = Configuration(configuration_id=f"benchmark-{num_components}")
    items = [
        BOMItem(
            component_id=f"COMP-{i}",
            quantity=1,
            origin_type=BOMOrigin.FEATURE,
            reason="Benchmark",
        )
        for i in range(num_components)
    ]
    config.bill_of_materials = BillOfMaterials(
        items=items, total_components=num_components
    )
    return config


@pytest.mark.parametrize("size", [100, 500, 1000])
def test_export_benchmarks_json(size):
    config = generate_large_configuration(size)
    exporter = JSONExporter()
    context = ExportContext(
        configuration=config,
        correlation_id=f"bench-{size}",
        execution_timestamp="2026-07-08T00:00:00Z",
        export_format=ExportFormat.JSON,
    )

    t0 = time.perf_counter()
    report = exporter.export(context)
    duration_ms = (time.perf_counter() - t0) * 1000

    assert report.success
    assert report.file_size > 0
    # Ensuring it completes within a reasonable threshold (e.g., 500ms even for 1000 components)
    assert duration_ms < 500.0
