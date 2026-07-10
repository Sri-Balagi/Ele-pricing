"""
Graph Validator.

Validates the structural integrity of a constructed DependencyGraph before
any traversal begins. This is distinct from DependencyValidator, which
validates raw catalogue data.

Rules:
  ERROR (halts traversal):
    - Self-loops: an edge where source == target
    - Invalid node references: an edge endpoint not in graph.nodes
    - Duplicate edges: same source→target with same dependency_type

  WARNING (continues, appended to report):
    - Orphan nodes: nodes with no inbound AND no outbound active edges
"""


from app.models.domain import DependencyGraph


class GraphValidationError(Exception):
    """Raised when the graph contains structural errors that prevent safe traversal."""

    pass


class GraphValidator:
    """Validates the structural integrity of a DependencyGraph."""

    def validate(self, graph: DependencyGraph) -> list[str]:
        """
        Validates the graph. Returns a list of warning strings (orphan nodes etc.).
        Raises GraphValidationError if any structural errors are found.
        """
        errors: list[str] = []
        warnings: list[str] = []

        self._check_self_loops(graph, errors)
        self._check_invalid_references(graph, errors)
        self._check_duplicate_edges(graph, errors)
        self._check_orphan_nodes(graph, warnings)

        if errors:
            raise GraphValidationError(
                f"Graph validation failed with {len(errors)} structural error(s):\n"
                + "\n".join(f"  • {e}" for e in errors)
            )

        return warnings

    # ── Error Checks (halt on failure) ────────────────────────────────────────

    def _check_self_loops(self, graph: DependencyGraph, errors: list[str]) -> None:
        for source_id, edges in graph.adjacency_list.items():
            for edge in edges:
                if edge.dependency.source_id == edge.dependency.target_id:
                    errors.append(
                        f"Self-loop detected: node '{source_id}' has a dependency on itself "
                        f"(dep ID: '{edge.dependency.id}')"
                    )

    def _check_invalid_references(
        self, graph: DependencyGraph, errors: list[str]
    ) -> None:
        for source_id, edges in graph.adjacency_list.items():
            for edge in edges:
                if edge.dependency.source_id not in graph.nodes:
                    errors.append(
                        f"Dependency '{edge.dependency.id}' references unknown source node "
                        f"'{edge.dependency.source_id}'"
                    )
                if edge.dependency.target_id not in graph.nodes:
                    errors.append(
                        f"Dependency '{edge.dependency.id}' references unknown target node "
                        f"'{edge.dependency.target_id}'"
                    )

    def _check_duplicate_edges(self, graph: DependencyGraph, errors: list[str]) -> None:
        seen: set[tuple[str, str, str]] = set()
        for source_id, edges in graph.adjacency_list.items():
            for edge in edges:
                key = (
                    edge.dependency.source_id,
                    edge.dependency.target_id,
                    edge.dependency.dependency_type,
                )
                if key in seen:
                    errors.append(
                        f"Duplicate edge: source='{key[0]}' target='{key[1]}' "
                        f"type='{key[2]}' (dep ID: '{edge.dependency.id}')"
                    )
                seen.add(key)

    # ── Warning Checks (continue on detection) ────────────────────────────────

    def _check_orphan_nodes(self, graph: DependencyGraph, warnings: list[str]) -> None:
        nodes_with_edges = set(graph.adjacency_list.keys()) | set(
            graph.reverse_adjacency.keys()
        )
        for node_id in graph.nodes:
            if node_id not in nodes_with_edges:
                warnings.append(
                    f"Orphan node detected: '{node_id}' has no inbound or outbound edges"
                )
