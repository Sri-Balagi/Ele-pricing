"""
Resolution Strategies.

Defines the BaseResolutionStrategy ABC and the default
TopologicalResolutionStrategy.

Design:
  - DependencyResolver selects a strategy at construction time
  - New strategies (e.g., PriorityResolutionStrategy) plug in without
    modifying DependencyResolver or ResolutionExecutor
  - Each strategy receives the DependencyResolutionContext and delegates
    individual node resolution to ResolutionExecutor
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from app.models.domain import DependencyResolutionContext

if TYPE_CHECKING:
    from app.dependency_engine.executor import ResolutionExecutor


class BaseResolutionStrategy(ABC):
    """Abstract base for dependency resolution traversal strategies."""

    @abstractmethod
    def execute(
        self,
        topo_order: list[str],
        reachable_set: set[str],
        context: DependencyResolutionContext,
        executor: "ResolutionExecutor",
    ) -> None:
        """
        Iterates over nodes in the appropriate order and delegates to executor.

        Args:
            topo_order: All nodes in topological order.
            reachable_set: Nodes reachable from the active configuration.
            context: Current resolution context (mutable).
            executor: ResolutionExecutor responsible for per-edge logic.
        """


class TopologicalResolutionStrategy(BaseResolutionStrategy):
    """
    Resolves dependencies in strict topological order.

    Only processes nodes that are reachable from the current configuration.
    Unreachable nodes are skipped and counted in metrics.
    """

    def execute(
        self,
        topo_order: list[str],
        reachable_set: set[str],
        context: DependencyResolutionContext,
        executor: "ResolutionExecutor",
    ) -> None:
        for node_id in topo_order:
            context.current_node_id = node_id

            if node_id not in reachable_set:
                context.report.metrics.skipped_nodes += 1
                continue

            context.report.metrics.traversed_nodes += 1

            for edge in context.graph.adjacency_list.get(node_id, []):
                if not edge.is_active:
                    continue
                context.current_edge = edge
                executor.apply(edge, context)
                context.current_edge = None

            context.report.metrics.resolved_nodes += 1
