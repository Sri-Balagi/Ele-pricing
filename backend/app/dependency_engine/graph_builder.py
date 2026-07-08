"""
Graph Builder.

Constructs a DependencyGraph topology from the DependencyRegistry and
Product Catalogue. Does not evaluate conditions or mutate Configuration.

Responsibilities:
  - Build DependencyNode set from catalogue entities
  - Build DependencyEdge set from registry dependencies
  - Populate node entity_type (COMPONENT | OPTION) from catalogue
  - Return an immutable topology (is_active defaults to True)
"""

from typing import List

from app.models.domain import (
    Dependency,
    DependencyEdge,
    DependencyGraph,
    DependencyNode,
    ProductCatalogue,
)
from app.dependency_engine.registry import DependencyRegistry


class GraphBuilder:
    """Builds the static DependencyGraph topology from the registry."""

    def __init__(self, catalogue: ProductCatalogue) -> None:
        self._catalogue = catalogue
        self._known_components = {c.id for c in catalogue.components}
        self._known_options = {o.id for o in catalogue.feature_options}

    def build(self, registry: DependencyRegistry) -> DependencyGraph:
        """
        Constructs and returns a fully populated DependencyGraph.
        All edges default to is_active=True; activation is performed separately.
        """
        deps = registry.get_all()
        graph = DependencyGraph(nodes={}, adjacency_list={}, reverse_adjacency={})

        for dep in deps:
            self._ensure_node(graph, dep.source_id)
            self._ensure_node(graph, dep.target_id)

            edge = DependencyEdge(dependency=dep, is_active=True)

            graph.adjacency_list.setdefault(dep.source_id, []).append(edge)
            graph.reverse_adjacency.setdefault(dep.target_id, []).append(edge)

        return graph

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _ensure_node(self, graph: DependencyGraph, entity_id: str) -> None:
        if entity_id not in graph.nodes:
            graph.nodes[entity_id] = DependencyNode(
                entity_id=entity_id,
                entity_type=self._resolve_type(entity_id),
            )

    def _resolve_type(self, entity_id: str) -> str:
        if entity_id in self._known_components:
            return "COMPONENT"
        if entity_id in self._known_options:
            return "OPTION"
        return "UNKNOWN"
