import pytest

from app.dependency_engine.graph_cache import GraphCache
from app.models.domain import (
    CatalogMetadata,
    Component,
    Dependency,
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
def base_catalogue():
    return ProductCatalogue(
        metadata=CatalogMetadata(
            catalogue_version="v1.0",
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
        ],
        feature_options=[],
        mappings=[],
        dependencies=[
            Dependency(
                id="D1",
                source_id="C1",
                target_id="C2",
                dependency_type=DependencyType.REQUIRES,
            )
        ],
        rules=[],
    )


def test_cache_miss_on_first_request(base_catalogue):
    cache = GraphCache()
    assert not cache.is_warm

    registry = MockRegistry(base_catalogue.dependencies)
    graph = cache.get_or_build(base_catalogue, registry)

    assert cache.is_warm
    assert cache.cached_version == "v1.0"
    assert "C1" in graph.nodes


def test_cache_hit_on_same_version(base_catalogue):
    cache = GraphCache()
    registry = MockRegistry(base_catalogue.dependencies)

    # First request
    g1 = cache.get_or_build(base_catalogue, registry)
    assert cache.is_warm

    # Mutate registry (but don't change version) to prove it uses cache
    registry._data.append(
        Dependency(
            id="D2",
            source_id="C2",
            target_id="C1",
            dependency_type=DependencyType.REQUIRES,
        )
    )

    # Second request
    g2 = cache.get_or_build(base_catalogue, registry)

    # Assert D2 is not in graph because it hit the cache
    assert len(g2.adjacency_list.get("C2", [])) == 0


def test_cache_invalidation_on_version_bump(base_catalogue):
    cache = GraphCache()
    registry = MockRegistry(base_catalogue.dependencies)

    cache.get_or_build(base_catalogue, registry)
    assert cache.cached_version == "v1.0"

    # Bump version
    base_catalogue.metadata.catalogue_version = "v1.1"
    base_catalogue.components.append(
        Component(id="C3", category="Cabin", name="C3", unit="pcs")
    )
    registry._data.append(
        Dependency(
            id="D2",
            source_id="C2",
            target_id="C3",
            dependency_type=DependencyType.REQUIRES,
        )
    )

    g2 = cache.get_or_build(base_catalogue, registry)
    assert cache.cached_version == "v1.1"
    assert "C3" in g2.nodes
    assert len(g2.adjacency_list.get("C2", [])) == 1
