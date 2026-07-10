import pytest

from app.dependency_engine.resolver import DependencyResolver
from app.models.domain import (
    CatalogMetadata,
    Component,
    Configuration,
    ConfigurationStatus,
    Dependency,
    DependencyResolutionContext,
    DependencyResolutionReport,
    DependencyType,
    ProductCatalogue,
)


class MockRegistry:
    def __init__(self, data):
        self._data = data

    def get_all(self):
        return self._data

    def get_outgoing(self, node_id):
        return [d for d in self._data if d.source_id == node_id]


@pytest.fixture
def adversarial_catalogue():
    return ProductCatalogue(
        metadata=CatalogMetadata(
            catalogue_version="v_adv",
            schema_version="1.0",
            created_date="2026-07-08T00:00:00Z",
            last_updated="2026-07-08T00:00:00Z",
            prototype_version="1.0",
        ),
        categories=[],
        feature_groups=[],
        features=[],
        components=[
            Component(id="C1", category="Cabin", name="C1", unit="pcs"),
            Component(id="C2", category="Cabin", name="C2", unit="pcs"),
            Component(id="C3", category="Cabin", name="C3", unit="pcs"),
        ],
        feature_options=[],
        mappings=[],
        dependencies=[
            # Cycle: C1 -> C2 -> C3 -> C1
            Dependency(
                id="D1",
                source_id="C1",
                target_id="C2",
                dependency_type=DependencyType.REQUIRES,
            ),
            Dependency(
                id="D2",
                source_id="C2",
                target_id="C3",
                dependency_type=DependencyType.REQUIRES,
            ),
            Dependency(
                id="D3",
                source_id="C3",
                target_id="C1",
                dependency_type=DependencyType.REQUIRES,
            ),
            # Missing component: C3 -> C_MISSING
            Dependency(
                id="D4",
                source_id="C3",
                target_id="C_MISSING",
                dependency_type=DependencyType.REQUIRES,
            ),
        ],
        rules=[],
    )


def test_validator_catches_missing_entity(adversarial_catalogue):
    registry = MockRegistry(adversarial_catalogue.dependencies)

    with pytest.raises(Exception) as exc_info:
        DependencyResolver(adversarial_catalogue, registry)

    assert "unknown target entity" in str(exc_info.value)


def test_dependency_engine_cycle_detection(adversarial_catalogue):
    # Remove the invalid dependency so it passes validation
    valid_deps = [
        d for d in adversarial_catalogue.dependencies if d.target_id != "C_MISSING"
    ]
    registry = MockRegistry(valid_deps)

    resolver = DependencyResolver(adversarial_catalogue, registry)

    config = Configuration(
        configuration_id="CFG-CYCLE",
        status=ConfigurationStatus.DRAFT,
        resolved_components=["C1"],  # Start traversal at C1
    )

    report = DependencyResolutionReport(configuration_id=config.configuration_id)
    ctx = DependencyResolutionContext(
        configuration=config,
        catalogue=adversarial_catalogue,
        report=report,
        correlation_id="corr-cycle",
        execution_timestamp="ts",
    )

    # Should safely terminate and report cycle
    res_report = resolver.resolve(ctx)

    # C2 and C3 should NOT be added because resolution aborts on cycle detection
    assert "C2" not in config.resolved_components
    assert "C3" not in config.resolved_components

    # Cycle detection is in DependencyResolver
    assert len(res_report.cycles_detected) > 0
