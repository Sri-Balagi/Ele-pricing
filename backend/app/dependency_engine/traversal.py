"""
Traversal Engine.

Activates a reachable subgraph from the current configuration using BFS,
then delegates topological sorting and cycle detection to CycleDetector.

Responsibilities:
  - BFS from the union of selected_feature_options + resolved_components
    to mark which nodes are reachable (part of the active configuration)
  - Wrap CycleDetector to obtain the topologically sorted traversal order
  - Return ordered list of (node_id, is_reachable) tuples for resolution

Design:
  - Operates on the already-activated graph (DependencyActivationEngine ran first)
  - Does NOT mutate Configuration
  - Reachability is determined only from active edges
"""

import logging

from app.dependency_engine.cycle_detector import CycleDetector
from app.models.domain import Configuration, DependencyGraph

logger = logging.getLogger(__name__)


class TraversalEngine:
    """BFS subgraph activation + topological traversal ordering."""

    def __init__(self) -> None:
        self._cycle_detector = CycleDetector()

    def get_traversal_order(
        self,
        graph: DependencyGraph,
        configuration: Configuration,
    ) -> tuple[list[str], set[str]]:
        """
        Computes the traversal order and the reachable node set.

        Returns:
            (topo_order, reachable_set)
            - topo_order: all graph nodes in dependency-safe order
            - reachable_set: nodes reachable from the configuration's active entities

        Raises:
            CircularDependencyError: if a cycle is detected.
        """
        reachable = self._bfs_reachable(graph, configuration)

        # Cycle detection also produces the topological order (reused, no double sort)
        topo_order = self._cycle_detector.check_and_sort(graph)

        logger.debug(
            "Traversal order computed: %d total nodes, %d reachable from configuration",
            len(topo_order),
            len(reachable),
        )
        return topo_order, reachable

    def _bfs_reachable(
        self, graph: DependencyGraph, configuration: Configuration
    ) -> set[str]:
        """
        BFS from the union of selected options and resolved components
        to determine which nodes are reachable through active REQUIRES edges.
        """
        seeds: set[str] = set(configuration.selected_feature_options) | set(
            configuration.resolved_components
        )
        visited: set[str] = set()
        queue = list(seeds & graph.nodes.keys())  # Only seeds that are graph nodes

        while queue:
            node_id = queue.pop()
            if node_id in visited:
                continue
            visited.add(node_id)

            for edge in graph.adjacency_list.get(node_id, []):
                if edge.is_active and edge.dependency.target_id not in visited:
                    queue.append(edge.dependency.target_id)

        return visited
