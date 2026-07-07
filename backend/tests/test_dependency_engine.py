import pytest
from app.models.domain import (
    Configuration, ProductCatalogue, CatalogMetadata, Dependency,
    ValidationResult, Component, FeatureOption
)
from app.core.constants import DependencyType, ConfigurationStatus, ComponentCategory, Unit
from app.dependency_engine.graph import GraphBuilder, CircularDependencyError
from app.dependency_engine.engine import DependencyEngine

@pytest.fixture
def mock_catalogue():
    return ProductCatalogue(
        metadata=CatalogMetadata(
            catalogue_version="1.0",
            schema_version="1.0",
            created_date="2026-07-07T00:00:00Z",
            last_updated="2026-07-07T00:00:00Z",
            prototype_version="1.0",
        ),
        categories=[],
        feature_groups=[],
        features=[],
        components=[
            Component(id="A", name="A", category=ComponentCategory.MECHANICAL, unit=Unit.PCS),
            Component(id="B", name="B", category=ComponentCategory.MECHANICAL, unit=Unit.PCS),
            Component(id="C", name="C", category=ComponentCategory.MECHANICAL, unit=Unit.PCS),
            Component(id="X", name="X", category=ComponentCategory.MECHANICAL, unit=Unit.PCS),
            Component(id="Y", name="Y", category=ComponentCategory.MECHANICAL, unit=Unit.PCS),
            Component(id="Z", name="Z", category=ComponentCategory.MECHANICAL, unit=Unit.PCS),
        ],
        feature_options=[
            FeatureOption(id="DO_Z", feature_id="F1", display_name="DO_Z", internal_value="true")
        ],
        mappings=[],
        dependencies=[
            Dependency(id="D1", source_id="A", target_id="B", dependency_type=DependencyType.REQUIRES),
            Dependency(id="D2", source_id="B", target_id="C", dependency_type=DependencyType.REQUIRES),
            Dependency(id="D3", source_id="X", target_id="Y", dependency_type=DependencyType.EXCLUDES),
            Dependency(
                id="D4", source_id="A", target_id="Z", 
                dependency_type=DependencyType.REQUIRES, 
                condition_expression="has_option('DO_Z')"
            ),
        ]
    )

@pytest.fixture
def mock_config():
    return Configuration(
        configuration_id="test-config",
        resolved_components=["A", "X"],
        selected_feature_options=[],
        validation_results=ValidationResult(is_valid=True)
    )

def test_topological_sort_success(mock_catalogue):
    graph = GraphBuilder.build_graph(mock_catalogue.dependencies)
    topo = GraphBuilder.get_topological_sort(graph)
    # A -> B -> C means A must come before B, B before C
    assert topo.index("A") < topo.index("B")
    assert topo.index("B") < topo.index("C")
    assert topo.index("X") < topo.index("Y")

def test_circular_dependency():
    deps = [
        Dependency(id="1", source_id="A", target_id="B", dependency_type=DependencyType.REQUIRES),
        Dependency(id="2", source_id="B", target_id="C", dependency_type=DependencyType.REQUIRES),
        Dependency(id="3", source_id="C", target_id="A", dependency_type=DependencyType.REQUIRES),
    ]
    graph = GraphBuilder.build_graph(deps)
    with pytest.raises(CircularDependencyError):
        GraphBuilder.get_topological_sort(graph)

def test_dependency_engine_resolution(mock_catalogue, mock_config):
    engine = DependencyEngine(mock_catalogue)
    report = engine.resolve(mock_config)
    
    # A requires B, B requires C. So B and C should be added.
    assert "B" in mock_config.resolved_components
    assert "C" in mock_config.resolved_components
    
    # Check mutations log
    assert any(m.entity_id == "B" and m.mutation_type == "ADDED" for m in mock_config.mutations)
    assert any(m.entity_id == "C" and m.mutation_type == "ADDED" for m in mock_config.mutations)

def test_dependency_engine_conflicts(mock_catalogue, mock_config):
    # Both X and Y are present, but X excludes Y.
    mock_config.resolved_components = ["X", "Y"]
    engine = DependencyEngine(mock_catalogue)
    report = engine.resolve(mock_config)
    
    assert len(report.conflicts_detected) == 1
    assert "Y" in report.conflicts_detected
    assert mock_config.validation_results.is_valid is False
    assert any(err.code == "DEP_CONFLICT" for err in mock_config.validation_results.errors)

def test_dependency_engine_conditional(mock_catalogue, mock_config):
    # A requires Z ONLY IF DO_Z option is selected
    mock_config.resolved_components = ["A"]
    engine = DependencyEngine(mock_catalogue)
    report = engine.resolve(mock_config)
    assert "Z" not in mock_config.resolved_components
    
    # Now select DO_Z
    mock_config.selected_feature_options = ["DO_Z"]
    report = engine.resolve(mock_config)
    assert "Z" in mock_config.resolved_components
