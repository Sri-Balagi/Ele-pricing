"""
Cycle Detector.

Uses Kahn's topological sort algorithm to detect circular dependencies.
If a cycle exists, Kahn's algorithm cannot process all nodes, and the
remaining nodes (those still with in-degree > 0) form the guilty set.

Design:
  - Operates only on ACTIVE edges (is_active=True)
  - Raises CircularDependencyError with the guilty node chain
  - Returns the topological order on success (reused by TraversalEngine)
"""

from collections import deque
from typing import Dict, List

from app.models.domain import DependencyGraph


class CircularDependencyError(Exception):
    """Raised when a cycle is detected in the active dependency graph."""

    def __init__(self, guilty_nodes: List[str]) -> None:
        self.guilty_nodes = guilty_nodes
        super().__init__(
            f"Circular dependency detected. Involved nodes: {guilty_nodes}"
        )


class CycleDetector:
    """Detects cycles in the dependency graph using Kahn's algorithm."""

    def check_and_sort(self, graph: DependencyGraph) -> List[str]:
        """
        Runs Kahn's algorithm on the active subgraph.

        Returns:
            Topologically sorted list of node IDs (all nodes, active subgraph order).

        Raises:
            CircularDependencyError: if any cycle is detected.
        """
        in_degree: Dict[str, int] = {node_id: 0 for node_id in graph.nodes}

        # Count in-degrees from active edges only
        for edges in graph.adjacency_list.values():
            for edge in edges:
                if edge.is_active:
                    in_degree[edge.dependency.target_id] += 1

        queue = deque(
            node_id for node_id, degree in in_degree.items() if degree == 0
        )
        topo_order: List[str] = []

        while queue:
            node_id = queue.popleft()
            topo_order.append(node_id)

            for edge in graph.adjacency_list.get(node_id, []):
                if edge.is_active:
                    target = edge.dependency.target_id
                    in_degree[target] -= 1
                    if in_degree[target] == 0:
                        queue.append(target)

        if len(topo_order) != len(graph.nodes):
            guilty = [n for n, d in in_degree.items() if d > 0]
            raise CircularDependencyError(guilty_nodes=guilty)

        return topo_order
